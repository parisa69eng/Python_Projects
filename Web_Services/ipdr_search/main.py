import os
import re
import datetime
import ipaddress
import binascii
import shutil
import logging
import struct
import socket
import gzip
import json
import time
from waitress import serve
from http import HTTPStatus
from datetime import timedelta
from flask import Flask, request, jsonify, Response


global SETTINGS

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)


def ipaddress_to_iphex(ip: str):
    h = ipaddress.IPv4Address(ip).packed
    hex_bytes = binascii.hexlify(h)
    return hex_bytes.decode("utf-8")


def iphex_to_ipaddress(iphex):
    addr_long = int(iphex, 16)
    hex(addr_long)
    struct.pack("<L", addr_long)
    ip = socket.inet_ntoa(struct.pack("<L", addr_long))
    ip_address_parts = ip.split(".")
    ip_address_parts.reverse()
    reversed_ip_address = ".".join(ip_address_parts)
    return reversed_ip_address


def delta(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    delta = dt.minute % 5
    if delta != 0:
        delta = 5 - delta
    return delta


def generate_time_for_file_name(from_date, to_date):
    start_time = datetime.datetime.fromtimestamp(from_date + delta(from_date) * 60)
    end_time = datetime.datetime.fromtimestamp(to_date + delta(to_date) * 60)
    if delta(to_date) != 0:
        end_time = end_time - datetime.timedelta(minutes=5)
    time_list = []
    while (start_time <= end_time):
        start_time = start_time+timedelta(minutes=5)
        start_time_str = start_time.strftime("%Y%m%d%H%M")
        time_list.append(start_time_str)

    return time_list


def generate_file_names(time_list):
    services = [4, 6]
    file_names = []
    for timestamp in time_list:
        for service in services:
            file_names.append(f"{timestamp}_{service}_FDI.csv.gz")
    return file_names


def process_file(file_name, ip, service_id,  SCRATCH_DIRECTORY, SOURCE_DIRECTORY):
    shutil.copy(os.path.join(SOURCE_DIRECTORY, file_name), SCRATCH_DIRECTORY)
    service_type = str(file_name).split("_")

    with gzip.open(os.path.join(SCRATCH_DIRECTORY, file_name), "rt") as f:
        file_content = f.read()
        ip_hex = ipaddress_to_iphex(ip)
        pattern = f".*{ip_hex}.*"
        if service_id:
            pattern = f"{service_id}" + pattern
        log_in_ipdr = re.findall(pattern, file_content)
        if not log_in_ipdr:
            logger.info("No log")
        output = []
        for log in log_in_ipdr:
            log = log.split('|')
            if len(log) < 15:
                continue
            if log[3] == '6':
                log[3] = "TCP"
            elif log[3] == '17':
                log[3] = "UDP"
            if service_type[1] == '6':
                service_type[1] = "TD_LTE"
            elif service_type[1] == '4':
                service_type[1] = "WIRELESS"
            elif service_type[1] == '15':
                service_type[1] = "DEDICATED_BROADBAND"
            result_log_in_ipdr = {"ipAddress": iphex_to_ipaddress(ip_hex), "macAddress": log[1], "serviceId": log[0], "serviceType": service_type[1],
                                  "sourceIpAddress": iphex_to_ipaddress(log[6]), "sourcePort": log[7], "targetIpAddress": iphex_to_ipaddress(log[8]),
                                  "targetPort": log[9], "layerThreeprotocol": "IPX", "layerFourprotocol": log[3]}
            output.append(result_log_in_ipdr)
        return output


def search_to_IPDR_files(IP, from_date, to_date, service_id):
    global SETTINGS
    time_list = generate_time_for_file_name(from_date, to_date)

    file_names = generate_file_names(time_list)

    if not os.path.exists(SETTINGS['scratch-directory']):
        os.mkdir(SETTINGS['scratch-directory'])
    output_final = []
    for file_name in file_names:
        if not os.path.exists(os.path.join(SETTINGS['source-directory'], file_name)):
            continue
        logger.info(f"start proccess file {file_name}")
        final = process_file(file_name, IP, service_id,
                             SETTINGS['scratch-directory'], SETTINGS['source-directory'])
        logger.info(f"finish proccess file {file_name} ")
        output_final.extend(final)
        os.remove(os.path.join(SETTINGS['scratch-directory'], file_name))

    return output_final


@app.route("/ipdr/", methods=['post'])
def ipdr_search():
    time_now = datetime.datetime.now()
    nine_months_ago = time_now - datetime.timedelta(days=9 * 30)
    nine_months_ago = int(time.mktime(nine_months_ago.timetuple()))
    content = request.json

    try:
        ip = content['IP']
        from_date = content['from_date']
        to_date = content['to_date']
    except:
        return Response(response=json.dumps({'message': "you should enter IP, from_date, to_date"}), status=HTTPStatus.BAD_REQUEST, content_type='application/json')

    try:
        ip = ipaddress.ip_address(ip)
    except:
        return Response(response=json.dumps({'message': 'invalid IP'}), status=HTTPStatus.BAD_REQUEST, content_type='application/json')

    if not ((from_date < to_date) and (from_date > nine_months_ago) and (to_date < time_now.timestamp())):
        return Response(response=json.dumps({'message': 'invalid date range'}), status=HTTPStatus.BAD_REQUEST, content_type='application/json')

    service_id = content.get('service_id')
    if service_id and len(service_id) != 36:
        return Response(response=json.dumps({'message': 'invalid service_id'}), status=HTTPStatus.BAD_REQUEST, content_type='application/json')

    result = search_to_IPDR_files(ip, from_date, to_date, service_id)

    if result:
        return Response(response=json.dumps(result), status=HTTPStatus.OK, content_type='application/json')

    return Response(response=json.dumps({'message': 'Not found'}), status=HTTPStatus.NOT_FOUND, content_type='application/json')


def setup_logger():
    global logger
    global SETTINGS

    if SETTINGS["log-level"] == "debug":
        logger.setLevel(logging.DEBUG)
    elif SETTINGS["log-level"] == "info":
        logger.setLevel(logging.INFO)
    elif SETTINGS["log-level"] == "warning":
        logger.setLevel(logging.WARNING)
    elif SETTINGS["log-level"] == "error":
        logger.setLevel(logging.ERROR)


def read_settings(settings_path):
    global SETTINGS
    with open(settings_path) as settings_file:
        SETTINGS = json.load(settings_file)


def main():
    SETTINGS_PATH = os.getenv('SETTINGS_PATH')
    read_settings(SETTINGS_PATH)
    setup_logger()
    serve(app, host=SETTINGS['flask']['host'], port=SETTINGS['flask']['port'])


if __name__ == '__main__':
    main()

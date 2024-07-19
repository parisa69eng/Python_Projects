import os
import logging
import json
import ipaddress
from flask import Flask, jsonify, request, Response
from waitress import serve
from http import HTTPStatus


global SETTINGS


app = Flask(__name__)

logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)


def get_last_imsi(ip, cdr_ip_directory):
    last_date = sorted(os.listdir(os.path.join(cdr_ip_directory, ip)))[-1]
    logger.info(f"last_date is {last_date}")
    logger.info(f"date_directory_path:{os.path.join(cdr_ip_directory, ip, last_date)}")
    last_log_file_name = sorted(os.listdir(os.path.join(cdr_ip_directory, ip, last_date)))[-1]
    logger.info(f"last_file is {last_log_file_name}")
    with open(os.path.join(os.path.join(cdr_ip_directory, ip, last_date), last_log_file_name)) as last_log_file:
        IMSI_INDEX = 1
        return last_log_file.read().split(',')[IMSI_INDEX]


def get_last_ip(imsi, cdr_imsi_directory):
    last_date = sorted(os.listdir(os.path.join(cdr_imsi_directory, str(imsi))))[-1]
    logger.info(f"last_date is {last_date}")
    logger.info(f"date_directory_path:{os.path.join(cdr_imsi_directory, str(imsi), last_date)}")
    last_log_file_name = sorted(os.listdir(os.path.join(cdr_imsi_directory, str(imsi), last_date)))[-1]
    logger.info(f"last_file is {last_log_file_name}")
    with open(os.path.join(os.path.join(cdr_imsi_directory, str(imsi), last_date), last_log_file_name)) as last_log_file:
        IP_INDEX = 5
        return last_log_file.read().split(',')[IP_INDEX]


@app.route("/last_imsi/<ip>")
def get_last_imsi_from_ip(ip):
    global SETTINGS
    logger.info(f"<{request.remote_addr}> Request received for {ip}")
    try:
        ip = str(ipaddress.IPv4Address(ip))
        last_imsi = get_last_imsi(ip, SETTINGS['cdr-ip-directory'])
        return jsonify({"ip": ip, "last_imsi": f"{last_imsi}"})
    except Exception as e:
        logger.error(e)
        return Response(response=json.dumps({'message': 'Not found'}), status=HTTPStatus.NOT_FOUND, content_type='application/json')


@app.route("/last_ip/<imsi>")
def get_last_ip_from_imsi(imsi):
    global SETTINGS
    logger.info(f"<{request.remote_addr}> Request received for {imsi}")
    try:
        last_ip = get_last_ip(imsi, SETTINGS['cdr-imsi-directory'])
        return jsonify({"imsi": imsi, "last_ip": f"{last_ip}"})
    except Exception as e:
        logger.error(e)
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
        try:
            SETTINGS = json.load(settings_file)
        except Exception as e:
            logger.error(e)
            exit(1)


def main():
    global SETTINGS

    SETTINGS_PATH = os.getenv('SETTINGS_PATH')
    read_settings(SETTINGS_PATH)
    setup_logger()
    serve(app, host=SETTINGS['flask']['host'], port=SETTINGS['flask']['port'])


if __name__ == '__main__':
    main()

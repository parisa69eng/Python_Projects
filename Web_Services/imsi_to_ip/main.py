import redis
from flask import Flask, json, jsonify
import logging
from waitress import serve
import os


global ip_to_imsi_redis_database
global imsi_to_ip_redis_database
global SETTINGS

logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__)


def get_belonged_ip(imsi):
    global ip_to_imsi_redis_database
    global imsi_to_ip_redis_database

    logger.info(f'Start processing to get IP from IMSI {imsi}')
    last_belonged_ip_of_imsi = imsi_to_ip_redis_database.get(imsi)

    if not last_belonged_ip_of_imsi:
        logger.error("IP of IMSI doesnot exist")
        return (f'{last_belonged_ip_of_imsi}', "input IMSI does not exist")

    logger.info(f'IP of IMSI is {last_belonged_ip_of_imsi}')
    last_belonged_ip_of_imsi = last_belonged_ip_of_imsi.decode("utf-8")
    last_belonged_imsi_of_ip = ip_to_imsi_redis_database.get(
        last_belonged_ip_of_imsi)

    if not last_belonged_imsi_of_ip:
        return (f'{last_belonged_ip_of_imsi}', "Inactive")

    last_belonged_imsi_of_ip = last_belonged_imsi_of_ip.decode("utf-8")
    if (imsi == last_belonged_imsi_of_ip):
        logger.info(
            f'this user is active with IP {last_belonged_ip_of_imsi} and this IMSI {imsi}')
        return (f'{last_belonged_ip_of_imsi}', "Active")
    else:
        return (f'{last_belonged_ip_of_imsi}', "Inactive")


@app.route('/imsis/<imsi>')
def get_belonged_ip_api(imsi):
    try:
        ip, status = get_belonged_ip(imsi)
        return jsonify({"IP": ip, "status": status})
    except:
        logger.error("given IMSI isnot valid")
        return jsonify({"IP": None, "status": "given IMSI isnot valid"})


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
    global imsi_to_ip_redis_database
    global ip_to_imsi_redis_database
    global SETTINGS
    try:
        with open(settings_path) as settings_file:
            SETTINGS = json.loads(settings_file.read())
    except Exception as e:
        logger.error(f'Failed to load settings : {e}')
        exit(1)
    imsi_to_ip_redis_database = redis.Redis(
        host=SETTINGS['redis']['host'], port=SETTINGS['redis']['port'], password=SETTINGS['redis']['password'],
        db=SETTINGS['redis']['imsi-to-ip-database-index'])
    ip_to_imsi_redis_database = redis.Redis(
        host=SETTINGS['redis']['host'], port=SETTINGS['redis']['port'], password=SETTINGS['redis']['password'],
        db=SETTINGS['redis']['ip-to-imsi-database-index'])


if __name__ == '__main__':
    SETTINGS_PATH = os.getenv('SETTINGS_PATH')
    read_settings(SETTINGS_PATH)
    setup_logger()
    serve(app, host=SETTINGS['flask']['host'], port=SETTINGS['flask']['port'])

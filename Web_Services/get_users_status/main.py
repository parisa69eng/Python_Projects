import redis
import os
import logging
from http import HTTPStatus
from waitress import serve
from flask import Flask, json, request, Response


logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)

SETTINGS: dict
app = Flask(__name__)


def is_user_active(imsi):
    ip_to_imsi_redis_database = redis.Redis(**SETTINGS['ip-to-imsi-redis'], decode_responses=True)
    imsi_to_ip_redis_database = redis.Redis(**SETTINGS['imsi-to-ip-redis'], decode_responses=True)

    belonged_ip_of_imsi = imsi_to_ip_redis_database.get(imsi)
    if not belonged_ip_of_imsi:
        logger.error(f'IP of {imsi} does not exist in imsi-to-ip-database')
        return False

    belonged_imsi_of_ip = ip_to_imsi_redis_database.get(belonged_ip_of_imsi)
    if imsi == belonged_imsi_of_ip:
        return True

    return False


def get_users_of_enodeb(enodeb_id):
    user_information_redis_database = redis.Redis(**SETTINGS['user-information-redis'], decode_responses=True)
    active_users = []
    inactive_users = []
    enodeb_id = int(enodeb_id)

    for imsi in user_information_redis_database.scan_iter('432*'):
        eci = user_information_redis_database.hget(imsi, 'Location.ECGI.ECI')
        enodeb_of_imsi = int(eci) >> 8
        if enodeb_of_imsi == enodeb_id:
            if is_user_active(imsi):
                active_users.append(imsi)
            inactive_users.append(imsi)

    return {'active_users': active_users, 'inactive_users': inactive_users}


def get_users_of_tac(tac):
    active_users = []
    inactive_users = []
    user_information_redis_database = redis.Redis(**SETTINGS['user-information-redis'], decode_responses=True)

    for imsi in user_information_redis_database.scan_iter('432*'):
        imsi_tac = user_information_redis_database.hget(imsi, 'Location.TAI.TAC')

        if imsi_tac == tac:
            if is_user_active(imsi):
                active_users.append(imsi)
            inactive_users.append(imsi)

    return {'active_users': active_users, 'inactive_users': inactive_users}


@app.route('/users_status/tacs/<tac>')
def get_users_in_tac(tac):
    logger.info(f'<{request.remote_addr}> Request received for {tac}')
    try:
        result = get_users_of_tac(tac)
        if result:
            return Response(response=json.dumps(result), status=HTTPStatus.OK, content_type='application/json')
        return Response(response=json.dumps({'message': 'Not found'}), status=HTTPStatus.NOT_FOUND, content_type='application/json')
    except Exception as e:
        return Response(response=json.dumps({'message': f'{e}'}), status=HTTPStatus.INTERNAL_SERVER_ERROR, content_type='application/json')


@app.route('/users_status/enodebs/<enodeb_id>')
def get_users_in_enodeb(enodeb_id):
    logger.info(f'<{request.remote_addr}> Request received for {enodeb_id}')
    try:
        result = get_users_of_enodeb(enodeb_id)
        if result:
            return Response(response=json.dumps(result), status=HTTPStatus.OK, content_type='application/json')
        return Response(response=json.dumps({'message': 'Not found'}), status=HTTPStatus.NOT_FOUND, content_type='application/json')
    except Exception as e:
        return Response(response=json.dumps({'message': f'{e}'}), status=HTTPStatus.INTERNAL_SERVER_ERROR, content_type='application/json')


def setup_logger():
    global logger
    global SETTINGS

    if SETTINGS['log-level'] == 'debug':
        logger.setLevel(logging.DEBUG)
    elif SETTINGS['log-level'] == 'info':
        logger.setLevel(logging.INFO)
    elif SETTINGS['log-level'] == 'warning':
        logger.setLevel(logging.WARNING)
    elif SETTINGS['log-level'] == 'error':
        logger.setLevel(logging.ERROR)


def read_settings(settings_path):
    global SETTINGS
    try:
        with open(settings_path) as settings_file:
            SETTINGS = json.loads(settings_file.read())
    except Exception as e:
        logger.error(f'Failed to load settings : {e}')
        exit(1)


if __name__ == '__main__':
    SETTINGS_PATH = os.getenv('SETTINGS_PATH')
    read_settings(SETTINGS_PATH)
    setup_logger()
    serve(app, host=SETTINGS['flask']['host'], port=SETTINGS['flask']['port'])

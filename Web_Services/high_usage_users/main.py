import logging
import os
from http import HTTPStatus
from waitress import serve
from datetime import datetime
from jdatetime import datetime as jdatetime
from flask import Flask, request, json, Response


logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


def convert_persian_to_gregorian_date(persian_date_str: str):
    gregorian_date = jdatetime.strptime(persian_date_str, '%Y-%m-%d').togregorian()
    return gregorian_date


def get_high_usage_users(volume_threshold, from_date, to_date):
    from_date = convert_persian_to_gregorian_date(from_date)
    to_date = convert_persian_to_gregorian_date(to_date)
    logger.info(f'getting high_usage_users {volume_threshold}, {from_date}, {to_date}')
    usage_by_imsi = {}
    UPLOAD_VALUE_INDEX, DOWNLOAD_VALUE_INDEX = -2, -3
    for root, directories, cdr_files in os.walk(SETTINGS['cdr-directory'], topdown=False, onerror=None, followlinks=True):
        if not len(cdr_files) or len(directories):
            continue
        imsi = root.split('/')[-2]
        if imsi not in usage_by_imsi:
            usage_by_imsi[imsi] = 0
        date_string = root.split('/')[-1]
        current_date = datetime.strptime(date_string, '%Y-%m-%d')
        if not from_date <= current_date <= to_date:
            continue
        usage = 0
        for file_name in cdr_files:
            with open(os.path.join(root, file_name), 'r') as my_file:
                log_cdr_file = my_file.read().split(',')
                usage += int(log_cdr_file[UPLOAD_VALUE_INDEX]) + int(log_cdr_file[DOWNLOAD_VALUE_INDEX])
                usage_by_imsi[imsi] += usage
    logger.info('reading cdr files finished')
    high_usage_by_imsi = {}
    for imsi, usage in usage_by_imsi.items():
        usage = usage/(1024**3)
        if usage >= volume_threshold:
            high_usage_by_imsi[imsi] = usage

    return high_usage_by_imsi


@app.route('/high_usage_users', methods=['POST'])
def get_high_usage_users_api():
    logger.info(f'<{request.remote_addr}> Request received ')
    content = request.json
    try:
        volume_threshold = content['volume_threshold']
        from_date = content['from_date']
        to_date = content['to_date']
        result = get_high_usage_users(volume_threshold, from_date, to_date)
        return Response(response=json.dumps(result),
                        status=HTTPStatus.OK, content_type='application/json')
    except KeyError as e:
        return Response(response=json.dumps({'message': f'bad request : {e}'}),
                        status=HTTPStatus.BAD_REQUEST, content_type='application/json')
    except Exception as e:
        return Response(response=json.dumps({'message': f'error : {e}'}),
                        status=HTTPStatus.INTERNAL_SERVER_ERROR, content_type='application/json')


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
        logger.error(e)
        exit(1)


if __name__ == '__main__':
    read_settings(os.getenv('SETTINGS_PATH'))
    setup_logger()
    serve(app, host=SETTINGS['flask']['host'], port=SETTINGS['flask']['port'])

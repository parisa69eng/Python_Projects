from waitress import serve
from datetime import datetime
import logging
from jdatetime import datetime as jdatetime
import pandas
import requests
import json
import xlsxwriter
import os

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

global SETTINGS
global COUCHBASE_ANALYTIC_URL
global SCRATCH_DIRECTORY


logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__)
cors = CORS(app)


def convert_persian_to_gregorian_date(persian_date_str: str):
    result = jdatetime.strptime(persian_date_str, '%Y-%m-%d').togregorian()

    return result


def is_timestamp(date: str):
    return date.isnumeric()


def get_user_usage(imsi: str, from_date: str, to_date: str, do_send_file: bool):

    if is_timestamp(from_date):
        start_timestamp = int(from_date)
        from_date_time = datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%d_%H:%M:%S')
    else:
        from_date_gregorian = convert_persian_to_gregorian_date(from_date)
        start_time = datetime.strptime('00:00:00', '%H:%M:%S').time()
        from_date_time = datetime.combine(from_date_gregorian, start_time)
        start_timestamp = datetime.timestamp(from_date_time)

    if is_timestamp(to_date):
        end_timestamp = int(to_date)
        to_date_time = datetime.fromtimestamp(end_timestamp).strftime('%Y-%m-%d_%H:%M:%S')
    else:
        to_date_gregorian = convert_persian_to_gregorian_date(to_date)
        end_time = datetime.strptime('23:59:59', '%H:%M:%S').time()
        to_date_time = datetime.combine(to_date_gregorian, end_time)
        end_timestamp = datetime.timestamp(to_date_time)

    logger.info(f'Start processing to get user usage {imsi} from {from_date_time} to {to_date_time}')

    try:
        body = {
            "statement": f"SELECT millis_to_tz(startTime*1000, 'Asia/Tehran') \
    start_time, millis_to_tz(stopTime*1000, 'Asia/Tehran') stop_time, imsi, serviceId, download,\
    upload FROM last6monthcdr WHERE imsi={imsi} AND (startTime >= {start_timestamp} OR stopTime > {start_timestamp}) AND \
    (startTime < {start_timestamp} OR stopTime <={end_timestamp} ) ORDER BY startTime",
            "pretty": "true",
            "client_context_id": "axyzgha"
        }
        header = {"Content-Type": "application/json"}
        couchbase_response = requests.post(url=COUCHBASE_ANALYTIC_URL, headers=header,
                                           json=body, auth=('user1', 'password1'))
    except Exception as e:
        logger.error('Something is wrong on processing  : Error: {}'.format(e))
        return None

    try:
        results = couchbase_response.json()['results']
    except Exception as e:
        logger.error(f'getting result from response failed : {e}')
        return None

    total_usage = {'upload': 0, 'download': 0}
    for usage in results:
        total_usage['upload'] += usage['upload']
        total_usage['download'] += usage['download']

    total_usage_entry = {
        "start_time": "",
        "stop_time": "",
        "imsi": "",
        "serviceId": "",
        "download": total_usage['download'],
        "upload": total_usage['upload']
    }
    results.append(total_usage_entry)

    data_frame = pandas.DataFrame(results)

    tmp_csv_file = SCRATCH_DIRECTORY + 'my_file.csv'
    data_frame.to_csv(tmp_csv_file, index=False, header=True)

    if do_send_file:
        data_frame = pandas.read_csv(tmp_csv_file)

        result_file_path = SCRATCH_DIRECTORY + f'{imsi}_{from_date}_{to_date}.xlsx'
        result_excel_file = pandas.ExcelWriter(result_file_path, engine='xlsxwriter')

        data_frame.to_excel(result_excel_file, index=None,
                            header=True, sheet_name=imsi, engine=xlsxwriter)

        result_excel_file.sheets[imsi].set_column(0, 0, 27)
        result_excel_file.sheets[imsi].set_column(1, 1, 35)
        result_excel_file.sheets[imsi].set_column(2, 2, 20)
        result_excel_file.sheets[imsi].set_column(3, 3, 45)
        result_excel_file.sheets[imsi].set_column(4, 4, 15)
        result_excel_file.sheets[imsi].set_column(5, 5, 15)

        result_excel_file.close()

        logger.info('User usage excel file is writed in {}'.format(result_excel_file))

        return result_file_path

    logger.info(f'User usage for user {imsi} is prepared for sending back in JSON.')
    with open(tmp_csv_file, 'r') as tmp_csv_usage_file:
        return [usage_line[:-1] for usage_line in tmp_csv_usage_file.readlines()[1:]]


@app.route("/cdrs/imsis/<imsi>", methods=['GET'])
def get_parameters(imsi):
    logger.info(f"<{request.remote_addr}> Request received for {imsi}")

    data = request.args.to_dict()
    from_date = data.get('from')
    to_date = data.get('to')
    do_send_file = data.get('file') and data.get('file') == "true"

    if (from_date > to_date):
        return jsonify({"message": f"{from_date}  is grater than {to_date}"}), 400

    user_usage = get_user_usage(imsi, from_date, to_date, do_send_file)

    if user_usage:
        if do_send_file:
            return send_file(user_usage, as_attachment=True)

        return app.response_class(response=json.dumps(user_usage), status=200, mimetype='application/json')
    else:
        return jsonify({"message": "couchbase_response is null"})


def setup_logger():
    global logger
    global SETTINGS

    logging.basicConfig(format='[%(levelname)8s]  [%(asctime)s]  %(message)s',
                        level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

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
    global COUCHBASE_ANALYTIC_URL
    global SCRATCH_DIRECTORY
    with open(settings_path) as settings_file:
        SETTINGS = json.load(settings_file)
        try:
            COUCHBASE_ANALYTIC_URL = SETTINGS['couchbase-analytic-url']
            SCRATCH_DIRECTORY = SETTINGS['scratch-directory']
        except Exception as e:
            logger.error(e)
            exit(1)


def main():
    global SCRATCH_DIRECTORY

    SETTINGS_PATH = os.getenv('SETTINGS_PATH')
    read_settings(SETTINGS_PATH)
    os.makedirs(SCRATCH_DIRECTORY, exist_ok=True)
    setup_logger()
    serve(app, host=SETTINGS['flask']['host'], port=SETTINGS['flask']['port'])


if __name__ == '__main__':
    main()

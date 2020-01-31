import datetime
import os


logfile_name = 'job.log'
# TODO do sth about this path
basedir = os.path.abspath(os.path.dirname(__file__))
run_path = f'{basedir}/image_builder/run'


def datetime_now_to_string():
    return datetime_to_str(datetime.datetime.now())


def datetime_to_str(timestamp: datetime.datetime):
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')


def str_to_datetime(time_str: str):
    return datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')
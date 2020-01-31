import json
from pathlib import Path

from app.main.service import ImageBuilderConfig


def check_status(session_token: str):
    path = f"{ImageBuilderConfig.run_path}/{session_token}/deploy.data"
    status = 'building'
    if Path(path).exists():
        status_json = json.load(open(path, 'r'))
        return status_json, 201 if status_json['state'] == 'done' else 500

    status_json = {
        'session_token': session_token,
        'state': status,
        'timestamp_start': "available in next version of image builder REST API"
    }
    return status_json, 202


def check_log(session_token: str):
    path = f"{ImageBuilderConfig.run_path}/{session_token}/log.log"

    if Path(path).exists():
        log_json = json.load(open(path, 'r'))
        print(json.dumps(log_json, indent=2))
        return log_json, 200

    response_object = {
        'status': 'fail',
        'message': 'Logfile not found.'
    }
    return response_object, 400

import json
import os
import shutil
import sys
from pathlib import Path

import ImageBuilderConfig


def main():
    run_path = sys.argv[1]
    session_token = sys.argv[2]
    logfile = sys.argv[3]
    timestamp_start = sys.argv[4]

    # reading logfile
    path_to_logfile = Path(run_path + "/" + logfile)
    with open(path_to_logfile, 'r') as file:
        logfile = file.readlines()
        log_str = "".join(logfile)

    failed_keywords = ["fail", "Traceback", "ERROR", "Error", "error"]
    state = "failed" if len([i for i in failed_keywords if i in log_str]) != 0 else "done"

    timestamp_end = ImageBuilderConfig.datetime_now_to_string()
    _json = dict()
    _json["session_token"] = session_token
    _json["state"] = state
    _json["timestamp_start"] = timestamp_start
    _json["timestamp_end"] = timestamp_end
    _json["log"] = log_str

    # create json_log
    logfile = json.dumps(_json, indent=2, sort_keys=False)

    # save logfile to database
    # TODO connect to database and save somehow
    # database.update_deployment_log(_id=_id, blueprint_token=blueprint_token, _log=logfile, session_token=session_token,
    #                                timestamp=timestamp_end)

    shutil.rmtree(run_path)
    os.mkdir(run_path)

    # leave json deploy.data or undeploy.data in deployment data dir
    _json.pop("log")
    with open(run_path + "/deploy.data", 'w') as file:
        file.write(json.dumps(_json, indent=2, sort_keys=False))

    # TODO put it into database
    with open(run_path + "/log.log", 'w') as file:
        file.write(logfile)




if __name__ == '__main__':
    main()
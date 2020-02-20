#!/bin/bash
run_path=$1
session_token=$2
logfile=$3
timestamp_start=$4


cd "$run_path" || exit

{
  echo "Launching docker_image_definition with xOpera"
  opera deploy --inputs inputs.yaml image_builder docker_image_definition.yaml
} &> "$logfile"

cd "../../scripts" || exit

python3 finalize_deployment.py "$run_path" "$session_token" "$logfile" "$timestamp_start"
import json
import requests
import time
from pathlib import Path

# image-builder client
# use Python >= 3.8


def build(base_url, path: str, verbose=False):
    build_params = json.load(open(path, 'r'))

    response = requests.post(f"{base_url}/build/", json=build_params)
    invocation_id = response.json()['invocation_id']

    print(f'{invocation_id=}')

    while (state := requests.get(f"{base_url}/status/{invocation_id}").json()['state']) not in ('success', 'failed'):
        if verbose:
            print(f'{state=}')
        time.sleep(3)
    response_json = requests.get(f"{base_url}/status/{invocation_id}").json()
    if verbose:
        print(json.dumps(response_json, indent=2))
    print(f"{response_json['state']} {response_json['timestamp_end']}")


if __name__ == '__main__':
    url = "http://localhost:8080/"
    path = "build-params/JSON/hello_world/"
    print(f"{path=}")
    to_build = list(Path(path).glob('*'))
    for i, json_path in enumerate(to_build):
        print(f"Building [{i+1:02}/{len(to_build):02}]: {json_path.name}")
        build(url, str(json_path))

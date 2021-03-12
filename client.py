import json
import requests
import time

# image-builder client
# use Python >= 3.8


def build(base_url, path: str):
    build_params = json.load(open(path, 'r'))

    response = requests.post(f"{base_url}/build/", json=build_params)
    invocation_id = response.json()['invocation_id']

    print(f'{invocation_id=}')

    while (state := requests.get(f"{base_url}/status/{invocation_id}").json()['state']) not in ('success', 'failed'):
        print(f'{state=}')
        time.sleep(3)

    print(json.dumps(requests.get(f"{base_url}/status/{invocation_id}").json(), indent=2))


if __name__ == '__main__':
    url = "http://localhost:8080/"
    json_path = "JSON-build-params/snow-uc/snowwatch-renderer.json"
    build(url, json_path)

import json
import os
from pathlib import Path

import yaml

from image_builder.api.openapi.models import BuildParams
from image_builder.api.service.image_builder_service import transform_build_params
from image_builder.api.settings import Settings


def json_to_yaml(json_dir: Path, yaml_dir: Path, registry_ip: str = 'localhost:5000'):
    """
    Converts JSON build params (for API) from json_dir to YAML input files (for TOSCA) and saves them to yaml_dir
    """
    Settings.registry_ip = registry_ip
    json_files = [path for path in json_dir.rglob('*') if path.is_file()]
    print('Converting...')
    for file_path in json_files:
        build_params = BuildParams.from_dict(json.load(file_path.open('r')))
        if not build_params.source or not build_params.target:
            print(f'Error: {file_path.relative_to(json_dir)}')
            continue
        transformed = transform_build_params(build_params)
        new_path = Path(str(file_path).replace(str(json_dir), str(yaml_dir)).replace('.json', '.yaml'))
        print(f'OK:    {file_path.relative_to(json_dir)}')
        if not new_path.parent.exists():
            os.makedirs(new_path.parent, exist_ok=True)
        yaml.dump(transformed, new_path.open('w'))
    print('done.')


if __name__ == '__main__':
    json_path = Path(__file__).parent / 'build-params' /'JSON_(API)'
    yaml_path = Path(__file__).parent / 'build-params' / 'YAML_(TOSCA)'
    json_to_yaml(json_path, yaml_path)

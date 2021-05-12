# image-builder
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SODALITE-EU_image-builder&metric=alert_status)](https://sonarcloud.io/dashboard?id=SODALITE-EU_image-builder)

Image builder contains components needed to build images within the SODALITE platform.

# How to use image-builder

## Examples
Every example is in two forms: [json](build-params/JSON_(API)) (for REST API) and [yaml](build-params/YAML_(TOSCA)) (for image-builder TOSCA template).

## GIT
The simplest option for building docker images is to provide git repository with app code and dockerfile.

```json
{
  "source_type": "git",
  "source_repo": {
      "url": "https://github.com/mihaTrajbaric/generic_repo"
    },
  "target_image_name": "image_git",
  "target_image_tag": "latest"
}
```
Image builder will assume repository contains Dockerfile in repo's root dir of default branch and will use it for workdir during building process.
It will build image with tag `test_image:latest`, which will be pushed to preconfigured docker registry.

### Additional options
Additional options for git mode include:
- git authentication
- version (branch name, tag name, HEAD)
- Name or relative path of dockerfile (default: Dockerfile)
- workdir (default: . )
```json
{
  "source_type": "git",
  "source_repo": {
      "url": "https://github.com/mihaTrajbaric/generic-repo-2",
      "username": "git_username",
      "password": "git_password_or_token",
      "dockerfile": "docker_dir/Dockerfile",
      "workdir": "code_dir",
      "version": "HEAD"
    },
  "target_image_name": "image_git",
  "target_image_tag": "additional_options"
}
```
## Dockerfile
### No build context
Image builder can build image from standalone dockerfile without any build context.
```json
{
  "source_type": "dockerfile",
  "source_url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile",
  "target_image_name": "image_dockerfile",
  "target_image_tag": "no_context"
}
```

### Build context
Image builder can add arbitrary git repository for build context. It will insert dockerfile into root door of repository.
```json
{
  "source_type": "dockerfile",
  "source_url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/python_build_context/Dockerfile",
  "build_context": {
      "url": "https://github.com/mihaTrajbaric/generic_docker_build_context.git"
    },
  "target_image_name": "image_dockerfile",
  "target_image_tag": "build_context"
}
```

### Additional options
Additional options for dockerfile mode:
- url authentication
- build_context options
    - git authentication
    - subdir (relative path inside repo where build must be run)

```json
{
  "source_type": "dockerfile",
  "source_url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile",
  "source_username": "source_username",
  "source_password": "source_password_or_token",
  "build_context": {
      "url": "https://github.com/mihaTrajbaric/image-builder-test-files",
      "username": "git_username",
      "password": "git_password",
      "subdir": "no_context"
    },
  "target_image_name": "image_dockerfile",
  "target_image_tag": "additional_options"
}
```

## TAR
This mode allows image builder to load already built image and push it to docker registry.
Docker image can be saved to tar archive with [docker load command](https://docs.docker.com/engine/reference/commandline/save/):

    docker save [image-name] > [tar-name].tar

```json
{
  "source_type": "tar",
  "source_url": "https://github.com/mihaTrajbaric/image-builder-test-files/blob/master/hello-world.tar?raw=true",
  "target_image_name": "image_tar",
  "target_image_tag": "latest"
}
```

## Converting json to yaml
Image builder can run as [REST API](#rest-api) with JSON build params or as [TOSCA template](#docker-image-definition) with YAML build_params.
Conversion can be done with [json_to_yaml.py](json_to_yaml.py). [Examples](#examples) are in both formats.

## REST API

### Openapi spec
Image Builder REST API is build using [Openapi specification](openapi-spec.yml).

### Prerequisites

    - Ubuntu 20.04
    - python 3.8 or newer
     
#### Access to docker registry

In order to be able to push built images out, `image-builder` needs access to a docker registry. The registry
itself can be public or private, with the appropriate access credentials provided. For development and testing
purposes, a local registry can be trivially deployed using a pre-built image:

```
$ docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

The locally deployed registry can then be accessed at `localhost:5000`. More information on deploying and
securing an image registry is available [here](https://docs.docker.com/registry/deploying/).

If the repository uses certificate-based client-server authentication, signed certificates must be installed in `/etc/docker/certs.d`.
See the [docker docs](https://docs.docker.com/engine/security/certificates/) for more infoformation.

### Config
REST API's configuration can be set by setting following environmental variables:

    - REGISTRY_IP: IP of docker registry. Default: localhost
    
### Local run
To run locally, use [docker compose](docker-compose.yml) or [local TOSCA template](image-builder-rest-blueprint/docker-local/service.yaml) with compliant orchestrator. It was tested with [opera==0.6.4](https://pypi.org/project/opera/0.6.4/)
#### Script installation
In order to proceed with local docker installation use `deploy_local.sh` script (for Ubuntu Linux distribution) that checks and installs all components required for deployment (pip, xOpera, Ansible Roles, etc), provides means for setting up input variables necessary for deployment and starts the deployment itself. 

### Remote deploy
REST API can be deployed remotely using [TOSCA template](image-builder-rest-blueprint/openstack/service.yaml) with compliant orchestrator, for instance [xOpera](https://github.com/xlab-si/xopera-opera).
#### Steps before deploy
1.  Install pip packages:
    
    `python3 -m pip install opera[openstack]==0.6.4 docker`

2.  Install ansible-playbooks:

    `ansible-galaxy install -r image-builder-rest-blueprint/requirements.yml --force`

3.  Clone [SODALITE iac-modules (Release 3.4.1)](https://github.com/SODALITE-EU/iac-modules/releases/tag/3.4.1):
    
    `git clone -b 3.4.1 https://github.com/SODALITE-EU/iac-modules.git image-builder-rest-blueprint/openstack/modules`

4.  Copy image-builder TOSCA library
    
    `cp -r image-builder-rest-blueprint/library/ image-builder-rest-blueprint/openstack/library/`

5.  Generate TLS certificate and key files
    
    ```shell script
    openssl genrsa -out image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.key 4096
    openssl req -new -x509 -key image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.key -out image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.crt
    cp image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.key image-builder-rest-blueprint/openstack/modules/misc/tls/artifacts/ca.key
    cp image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.crt image-builder-rest-blueprint/openstack/modules/misc/tls/artifacts/ca.crt
    ```
### Sample JSON payloads
Sample JSON payloads to be used with `/build/` endpoint can be found in [build-params/JSON_(API)](build-params/JSON_(API)).

### Python client
Convenient Python client (Python 3.8) can send json payload and waits for the response (see [client.py](client.py)).

## docker-image-definition
docker-image-definition is a TOSCA blueprint, based on tosca_simple_yaml_1_3.
### Running using xOpera
Within SODALITE platform, it is executed with [xOpera orchestrator](https://github.com/xlab-si/xopera-opera).
If using xOpera 0.6.4 via CLI:
    
    opera deploy -i inputs.yaml docker_image_definition.yaml

### Running using the image builder CLI

It is also possible to run the image builder in a self-contained container using a CLI convenience wrapper:
    
```shell script
$ image-builder-cli.sh <input.yaml>
```

#### Building the image builder CLI

By default, the included `image-builder-cli.sh` script will use the `sodaliteh2020/image-builder-cli` image. If
developing the image builder locally, local versions of the CLI container can be built with the supplied Dockerfile:

```
$ cd REST_API && docker build -t <your tag> -f Dockerfile-cli .
```

you will then need to fix up the image name in the `image-builder-cli.sh` script to use your local image.

### build_params for docker-image-definition
docker-image-definition needs build_params in YAML format, which can be [converted](#converting-json-to-yaml) from json.

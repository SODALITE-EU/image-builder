# image-builder
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SODALITE-EU_image-builder&metric=alert_status)](https://sonarcloud.io/dashboard?id=SODALITE-EU_image-builder)

Image builder contains components needed to build images within the SODALITE platform.

# How to use image-builder

## Examples
Every example is in two forms: [json](build-params/JSON) (for REST API) and [yaml](build-params/YAML) (for image-builder TOSCA template).

## GIT
The simplest option for building docker images is to provide git repository with app code and dockerfile.

```json
{
  "source": {
    "git_repo": {
      "url": "https://github.com/mihaTrajbaric/generic_repo.git"
    }
  },
  "target": {
    "images": [
      {
        "image": "image_git",
        "tag": "latest"
      }
    ]
  }
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
  "source": {
    "git_repo": {
      "url": "https://github.com/mihaTrajbaric/generic-repo-2",
      "version": "HEAD",
      "username": "git_username",
      "password": "git_password_or_token",
      "dockerfile": "docker_dir/Dockerfile",
      "workdir": "code_dir"
    }
  },
  "target": {
    "images": [
      {
        "image": "image_git",
        "tag": "additional_options"
      }
    ]
  }
}
```
## Dockerfile
### No build context
Image builder can build image from standalone dockerfile without any build context.
```json
{
  "source": {
    "dockerfile": {
      "url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile"
    }
  },
  "target": {
    "images": [
      {
        "image": "dockerfile_no_context",
        "tag": "latest"
      }
    ]
  }
}
```

### Build context
Image builder can add arbitrary git repository for build context. It will insert dockerfile into root dir of repository.
```json
{
  "source": {
    "dockerfile": {
      "url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/python_build_context/Dockerfile"
    },
    "build_context": {
      "url": "https://github.com/mihaTrajbaric/generic_docker_build_context.git"
    }
  },
  "target": {
    "images": [
      {
        "image": "dockerfile_build-context",
        "tag": "latest"
      }
    ]
  }
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
  "source": {
    "dockerfile": {
      "url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile"
      "username": "username",
      "password": "password_or_token"
    },
    "build_context": {
      "subdir": "no_context",
      "url": "https://github.com/mihaTrajbaric/image-builder-test-files",
      "username": "git_username",
      "password": "git_password"
    }
  },
  "target": {
    "images": [
      {
        "image": "tests/subdir_context",
        "tag": "latest"
      }
    ]
  }
}

```

## Image variants
This mode enables image builder to build more variants of single docker image. Image variants are built by overloading 
the base container image, which is injected dynamically at build-time by the image builder, both for single and 
multi-stage builds. No modifications to the Dockerfile are required.

This mode works in combination with any of other modes (dockerfile, git, tar).

Following example will produce two images. `image_variants:latest` will be built with default bas image (specified 
in Dockerfile), while `image_variants:python-3.8` will be built on top of `python:3.8-alpine`.

```json

{
  "source": {
    "dockerfile": {
      "url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile"
    }
  },
  "target": {
    "images": [
      {
        "image": "image_variants",
        "tag": "latest"
      },
      {
        "image": "image_variants",
        "tag": "python-3.8",
        "base": "python:3.8-alpine"
      }
    ]
  }
}

```
## Multi-arch build
Image builder is capable of building images for multiple architectures leveraging [docker buildx](https://docs.docker.com/buildx/working-with-buildx/#build-multi-platform-images).

Following example will produce multiple variants of single image.

```json
{
  "source": {
    "dockerfile": {
      "url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile"
    }
  },
  "target": {
    "images": [
      {
        "image": "multi-arch",
        "tag": "latest",
        "platforms": [
          "linux/amd64",
          "linux/386",
          "linux/arm64",
          "linux/ppc64le",
          "linux/s390x",
          "linux/arm/v7",
          "linux/arm/v6"
        ]
      }
    ]
  }
}
```

Platforms are defined on per-image basis, so every image variant can target different set of platforms:
```json
{
  "source": {
    "git_repo": {
      "url": "https://github.com/mihaTrajbaric/generic_repo.git"
    }
  },
  "target": {
    "images": [
    {
      "image": "multi-arch",
      "tag": "latest",
      "platforms": [
        "linux/s390x",
        "linux/arm/v7",
        "linux/arm/v6"
      ]
    },
    {
      "image": "multi-arch",
      "tag": "python-3.8",
      "base": "python:3.8-alpine",
      "platforms": [
        "linux/amd64",
        "linux/386",
        "linux/arm64"
      ]
    }
  ]
  }
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
See the [docker docs](https://docs.docker.com/engine/security/certificates/) for more information.

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
    
    `python3 -m pip install opera[openstack]==0.6.6 docker`

2.  Install ansible-playbooks:

    `ansible-galaxy install -r image-builder-rest-blueprint/requirements.yml --force`

3.  Clone [SODALITE iac-modules (Release 3.4.1)](https://github.com/SODALITE-EU/iac-modules/releases/tag/3.5.0):
    
    `git clone -b 3.5.0 https://github.com/SODALITE-EU/iac-modules.git image-builder-rest-blueprint/openstack/modules`

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
Sample JSON payloads to be used with `/build/` endpoint can be found in [build-params/JSON_(API)](build-params/JSON).

### Python client
Convenient Python client (Python 3.8) can send json payload and waits for the response (see [client.py](client.py)).

## docker-image-definition
docker-image-definition is a TOSCA blueprint, based on tosca_simple_yaml_1_3.
### Running using xOpera
Within SODALITE platform, it is executed with [xOpera orchestrator](https://github.com/xlab-si/xopera-opera).
If using xOpera 0.6.6 via CLI:
    
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

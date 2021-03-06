# image-builder
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SODALITE-EU_image-builder&metric=alert_status)](https://sonarcloud.io/dashboard?id=SODALITE-EU_image-builder)

Image builder contains components needed to build images within the SODALITE platform.
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

### How to use image builder
#### Examples
Every example is in tree forms: [json](src/image_builder/TOSCA/playbooks/tests/tests-json) (for REST API), [yaml](src/image_builder/TOSCA/playbooks/tests/tests-yaml) (for image-builder TOSCA template) and [http-request](api-calls.http).

#### TAR
This mode allows image builder to load already built images and push them to docker registry.
Docker image can be saved to tar archive with [docker load command](https://docs.docker.com/engine/reference/commandline/save/):

    docker save [image-name] > [tar-name].tar

File inputs.yaml for this mode should follow this template:
    
    source:
      type: tar [required]
      url: https://url/to/tar/my_image.tar [required]
      username: my_username [optional]
      password: my_password_or_token [optional]

    target:
      registry_ip: my_registry_ip [required]
      image_name: my_image_name [required]
      image_tag: my_image_tag [required]
 
Notes:
  - source.url can lead to local file (`file:///path/to/local/image.tar`) or remote file (`https://url/to/tar/my_image.tar`)
  - source.username and source.url are optional
  - computer must have push access to registry
  - image is pushed to `[registry_ip]/[image_name]:[image_tag]`

#### Dockerfile - single image
This mode builds docker-image from Dockerfile with optional additional build context. Result is single docker image.

File inputs.yaml for this mode should follow this template:
    
    source:
        type: dockerfile [required]
        url: file:///path/to/Dockerfile [required]
        username: my_username [optional]
        password: my_password [optional]
        build_context: [optional]
            dir_name: build_context_dir_name [required]
 
            # local build context
            path: /path/to/local/build/context [required with local build context]

            # for Git build context
            url: https://url/to/git/repo.git [required with Git build context]
            subdir: path/to/subdir [optional]
            username: my_username [optional]
            password: my_password_or_token [optional]


    target:
        registry_ip: my_registry_ip [required]
        image_name: my_image_name [required]
        image_tag: my_image_tag [required]

Notes:
  - source.url can lead to local file (`file:///path/to/local/image.tar`) or remote file (`https://url/to/tar/my_image.tar`)
  - source.username and source.url are optional
  - build context is optional and can be either local directory or Git repository
  - computer must have push access to registry
  - image is pushed to `[registry_ip]/[image_name]:[image_tag]`

#### Dockerfile - image variants
This mode builds docker-image from Dockerfile with optional additional build context. Result are one or more image variants.
Image variants are built by overloading the base container image, which is injected dynamically at build-time by the
image builder, both for single and multi-stage builds. No modifications to the Dockerfile are required.

File inputs.yaml for this mode should follow this template:
    
    source:
        type: dockerfile [required]
        url: file:///path/to/Dockerfile [required]
        username: my_username [optional]
        password: my_password [optional]
        build_context: [optional]
            dir_name: build_context_dir_name [required]
 
            # local build context
            path: /path/to/local/build/context [required with local build context]

            # for Git build context
            url: https://url/to/git/repo.git [required with Git build context]
            subdir: path/to/subdir [optional]
            username: my_username [optional]
            password: my_password_or_token [optional]


    target:
        images: [required, one or more]
            - image: my_image_name [required]
              tag: my_image_tag [required]
        
            - image: my_image_name [required]
              tag: my_image_variant_tag [required]
              base: my_image_variant_base_image [optional]

 
Notes:
- source.url can lead to local file (`file:///path/to/local/image.tar`) or remote file (`https://url/to/tar/my_image.tar`)
- source.username and source.url are optional
- build context is optional and can be either local directory or Git repository
- computer must have push access to registry
- target image can use default base image (specified in Dockerfile) with `image` and `tag` params
- target image can use another base image with `image` and `tag` and `base` params
- all images are pushed to `[registry_ip]/[image]:[tag]`

### Tests
Tests can be run from [TOSCA](src/image_builder/TOSCA/playbooks) directory with:

    ./test.sh <registry_ip>

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
Sample JSON payloads to be used with `/build/` endpoint can be found in [JSON-build-params](JSON-build-params).

### Python client
Convenianc Python client (Python 3.8) can send json payload and waits for the response (see [client.py](client.py)).


# image-builder
Image builder contains components needed to build images within the SODALITE platform.
## docker-image-definition
docker-image-definition is a TOSCA blueprint, based on tosca_simple_yaml_1_2.
### Running using xOpera
Within SODALITE platform, it is executed with [xOpera orchestrator](https://github.com/xlab-si/xopera-opera).
If using xOpera 1.7 via CLI:
    
    sudo opera -i inputs.yaml image_builder docker_image_definition.yaml    

### Sample inputs
Inputs for [building from dockerfile](docker-image-definition/inputs_dockerfile.yaml) or [loading image from tar archive](docker-image-definition/inputs_tar.yaml).

## REST API

### Prerequisites

    - Ubuntu 18.04
    - python 3.6 or newer
     
#### Access to docker registry
In order to be able to push built docker images to docker registry, image-builder REST API needs access to registry.
If repository uses certificate-based client-server authentication, signed certificates must be installed to `/etc/docker/certs.d`.
See [docker docs](https://docs.docker.com/engine/security/certificates/) for more info.


### Config
REST API's configuration can be set by setting following environmental variables:
    
    - SECRET_KEY: key to be used for encoding / decoding Bearer tokens. Default: "my_precious_secret_key"
    - SESSION_TIMEOUT: time (in minutes) before Bearer token expires. Default: 1440 (1 day)
    - REGISTRY_IP: IP of docker registry. Default: localhost
    - SQLALCHEMY_DATABASE_URI: link to database. If left unset, local SQLITE instance will be configured and used.
    
### Install and run
#### Run in venv (optional, recommended)
- Installing: `python3 -m pip install --user virtualenv`
- Creating: `python3 -m venv [venv_name]`
- Activating: `source [venv_name]/bin/activate`


Your python venv must be activated before installation and also before every run.

#### Quick install and run
To install, test and run, simply run:

    make all
    
or run stages separately:
    
    make clean
    make install
    make database
    make tests
    make run
    





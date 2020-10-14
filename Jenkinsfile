pipeline {
    agent { label 'docker-slave' }
       environment {
       docker_registry_ip = credentials('jenkins-docker-registry-ip')
       OS_PROJECT_DOMAIN_NAME = "Default"
       OS_USER_DOMAIN_NAME = "Default"
       OS_PROJECT_NAME = "orchestrator"
       OS_TENANT_NAME = "orchestrator"
       OS_USERNAME = credentials('os-username')
       OS_PASSWORD = credentials('os-password')
       OS_AUTH_URL = credentials('os-auth-url')
       OS_INTERFACE = "public"
       OS_IDENTITY_API_VERSION = "3"
       OS_REGION_NAME = "RegionOne"
       OS_AUTH_PLUGIN = "password"
       ssh_key_name = "jenkins-opera"
       image_name = "centos7"
       network_name = "orchestrator-network"
       security_groups = "default,sodalite-remote-access,sodalite-rest"
       flavor_name = "m1.medium"
       ca_crt_file = credentials('xopera-ca-crt')
       ca_key_file = credentials('xopera-ca-key')
       ansible_python_interpreter = "/usr/bin/python3"
   }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Test image-builder'){
            steps {
                sh  """ #!/bin/bash
                        python3 -m venv venv-test
                        . venv-test/bin/activate
                        cd REST_API/
                        python3 -m pip install -r requirements.txt
                        cd app/
                        touch *.xml
                        python3 -m pytest --registry_ip $docker_registry_ip --pyargs -s test --junitxml="results.xml" --cov=./ --cov=./main/controller --cov=./main/model --cov=./main/service --cov=./main/util  --cov=./main --cov-report xml test/
                    """
                   junit 'REST_API/app/results.xml'
             }
        }
        stage('SonarQube analysis'){
            environment {
            scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh  """ #!/bin/bash
                            cd REST_API/app/
                            ${scannerHome}/bin/sonar-scanner
                        """
                }
            }
        }
        stage('Build and push image-builder-flask') {
            when { tag "*" }
            steps {
                sh """#!/bin/bash
                    cd REST_API
                    docker build -t image-builder-flask -f Dockerfile-flask .
                    docker tag image-builder-flask $docker_registry_ip/image-builder-flask
                    docker push $docker_registry_ip/image-builder-flask
                   """
            }
        }
        stage('Build and push image-builder-nginx') {
            when { tag "*" }
            steps {
                sh """#!/bin/bash
                    cd REST_API
                    docker build -t image-builder-nginx -f Dockerfile-nginx .
                    docker tag image-builder-nginx $docker_registry_ip/image-builder-nginx
                    docker push $docker_registry_ip/image-builder-nginx
                   """
            }
        }
        stage('Build and push image-builder-cli') {
            when { tag "*" }
            steps {
                sh """#!/bin/bash
                    cd REST_API
                    docker build -t image-builder-cli -f Dockerfile-cli .
                    docker tag image-builder-cli $docker_registry_ip/image-builder-cli
                    docker push $docker_registry_ip/image-builder-cli
                   """
            }
        }
        stage('Push image-builder-flask to DockerHub') {
            when { tag "*" }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            docker tag image-builder-flask sodaliteh2020/image-builder-flask
                            git fetch --tags
                            ./make_docker.sh push sodaliteh2020/image-builder-flask
                        """
                }
            }
        }
        stage('Push image-builder-nginx to DockerHub') {
            when { tag "*" }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            docker tag image-builder-nginx sodaliteh2020/image-builder-nginx
                            git fetch --tags
                            ./make_docker.sh push sodaliteh2020/image-builder-nginx
                        """
                }
            }
        }
        stage('Push image-builder-cli to DockerHub') {
            when { tag "*" }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            docker tag image-builder-cli sodaliteh2020/image-builder-cli
                            git fetch --tags
                            ./make_docker.sh push sodaliteh2020/image-builder-cli
                        """
                }
            }
        }
        stage('Install dependencies') {
            when { tag "*" }
            steps {
                sh """#!/bin/bash
                      python3 -m venv venv-deploy
                       . venv-deploy/bin/activate
                      python3 -m pip install --upgrade pip
                      python3 -m pip install 'opera[openstack]<0.5' docker
                      ansible-galaxy install -r REST_API/requirements.yml
                   """
            }
        }
        stage('Deploy to openstack') {
            when { tag "*" }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        truncate -s 0 image-builder-rest-blueprint/input.yaml
                        envsubst < image-builder-rest-blueprint/input.yaml.tmpl > image-builder-rest-blueprint/input.yaml
                        cat image-builder-rest-blueprint/input.yaml
                        . venv-deploy/bin/activate
                        cd image-builder-rest-blueprint
                        opera deploy -i input.yaml image-builder service.yaml
                       """
                }
            }
        }
    }
}

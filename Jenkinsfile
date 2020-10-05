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
        /*
        stage('Test core engine') {
            steps {
                sh  """#!/bin/bash
                        virtualenv venv-test
                        . venv-test/bin/activate
                        python3 -m pip install --upgrade pip
                        python3 -m pip install ansible docker requests
                        ansible-galaxy install -r REST_API/requirements.yml
                        cd REST_API/app/main/service/image_builder/TOSCA/playbooks
                        ./test.sh $docker_registry_ip
                     """
            }
        }
        */

        stage('Test API'){
            steps {
                sh  """ #!/bin/bash
                        virtualenv venv
                        . venv/bin/activate
                        cd REST_API/
                        pip3 install -r requirements.txt
                        cd app/
                        touch *.xml
                        python3 -m pytest --pyargs -s tests --junitxml="results.xml" --cov=./ --cov=./main/controller --cov=./main/model --cov=./main/service --cov=./main/util  --cov=./main --cov-report xml tests/
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
                sh "cd REST_API; docker build -t image-builder-flask -f Dockerfile-flask ."
                sh "docker tag image-builder-flask $docker_registry_ip/image-builder-flask"
                sh "docker push $docker_registry_ip/image-builder-flask"
            }
        }
        stage('Build and push image-builder-nginx') {
            when { tag "*" }
            steps {
                sh "cd REST_API; docker build -t image-builder-nginx -f Dockerfile-nginx ."
                sh "docker tag image-builder-nginx $docker_registry_ip/image-builder-nginx"
                sh "docker push $docker_registry_ip/image-builder-nginx"
            }
        }
        stage('Build and push image-builder-cli') {
            when { tag "*" }
            steps {
                sh "cd REST_API; docker build -t image-builder-cli -f Dockerfile-cli ."
                sh "docker tag image-builder-cli $docker_registry_ip/image-builder-cli"
                sh "docker push $docker_registry_ip/image-builder-cli"
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
                sh "virtualenv venv"
                sh ". venv/bin/activate; python -m pip install --upgrade pip"
                sh ". venv/bin/activate; python -m pip install -U 'opera[openstack]<0.5'"
                sh ". venv/bin/activate; python -m pip install docker"
                sh ". venv/bin/activate; ansible-galaxy install -r REST_API/requirements.yml"
            }
        }
        stage('Deploy to openstack') {
            when { tag "*" }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh 'truncate -s 0 image-builder-rest-blueprint/input.yaml'
                    sh 'echo "ssh-key-name: ${ssh_key_name}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "image-name: ${image_name}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "network-name: ${network_name}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "security-groups: ${security_groups}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "flavor-name: ${flavor_name}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "docker-registry-ip: ${docker_registry_ip}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "identity_file: ${xOpera_ssh_key_file}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "ca_crt_location: ${ca_crt_file}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'echo "ca_key_location: ${ca_key_file}" >> image-builder-rest-blueprint/input.yaml'
                    sh 'cat image-builder-rest-blueprint/input.yaml'
                    sh ". venv/bin/activate; cd image-builder-rest-blueprint; opera deploy -i input.yaml image-builder service.yaml"
                }
            }
        }
    }
}

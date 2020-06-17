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
   }
    
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Build and push image-builder-flask') {
            steps {
                sh "cd REST_API; docker build -t image-builder-flask -f Dockerfile-flask ."
                sh "docker tag image-builder-flask $docker_registry_ip/image-builder-flask"
                sh "docker push $docker_registry_ip/image-builder-flask"
            }
        }
        stage('Build and push image-builder-nginx') {
            steps {
                sh "cd REST_API; docker build -t image-builder-nginx -f Dockerfile-nginx ."
                sh "docker tag image-builder-nginx $docker_registry_ip/image-builder-nginx"
                sh "docker push $docker_registry_ip/image-builder-nginx"
            }
        }
        stage('Install dependencies') {
            steps {
                sh "virtualenv venv"
                sh ". venv/bin/activate; python -m pip install --upgrade pip"
                sh ". venv/bin/activate; python -m pip install -U 'opera[openstack]<0.5'"
                sh ". venv/bin/activate; python -m pip install docker"
                sh ". venv/bin/activate; ansible-galaxy install -r REST_API/requirements.yml"
            }
        }
        stage('Deploy to openstack') {
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

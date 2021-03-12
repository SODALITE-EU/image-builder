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

       // CI-CD vars
       // When triggered from git tag, $BRANCH_NAME is actually tag_name
       TAG_SEM_VER_COMPLIANT = """${sh(
                returnStdout: true,
                script: './validate_tag.sh SemVar $BRANCH_NAME'
            )}"""

       TAG_MAJOR_RELEASE = """${sh(
                returnStdout: true,
                script: './validate_tag.sh MajRel $BRANCH_NAME'
            )}"""

       TAG_PRODUCTION = """${sh(
                returnStdout: true,
                script: './validate_tag.sh production $BRANCH_NAME'
            )}"""

       TAG_STAGING = """${sh(
                returnStdout: true,
                script: './validate_tag.sh staging $BRANCH_NAME'
            )}"""
   }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Inspect GIT TAG'){
            steps {
                sh """ #!/bin/bash
                echo 'TAG: $BRANCH_NAME'
                echo 'Tag is compliant with SemVar 2.0.0: $TAG_SEM_VER_COMPLIANT'
                echo 'Tag is Major release: $TAG_MAJOR_RELEASE'
                echo 'Tag is production: $TAG_PRODUCTION'
                echo 'Tag is staging: $TAG_STAGING'
                """
            }

        }

        stage('Test image-builder'){
            steps {
                sh  """ #!/bin/bash
                        python3 -m venv venv-test
                        . venv-test/bin/activate
                        cd REST_API/
                        python3 -m pip install --upgrade pip
                        python3 -m pip install -r requirements.txt
                        cd app/
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
        stage('Build image-builder-api') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
             }
            steps {
                sh """#!/bin/bash
                    cd REST_API
                    ../make_docker.sh build image-builder-api Dockerfile
                    """
            }
        }
        stage('Build image-builder-cli') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
             }
            steps {
                sh """#!/bin/bash
                    cd REST_API
                    ../make_docker.sh build image-builder-cli Dockerfile-cli
                    """
            }
        }
        stage('Push image-builder-api to sodalite-private-registry') {
            // Push during staging and production
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push image-builder-api staging
                        """
                }
            }
        }
        stage('Push image-builder-cli to sodalite-private-registry') {
            // Push during staging and production
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push image-builder-cli staging
                        """
                }
            }
        }
        stage('Push image-builder-api to DockerHub') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push image-builder-api production
                        """
                }
            }
        }
        stage('Push image-builder-cli to DockerHub') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push image-builder-cli production
                        """
                }
            }
        }
        stage('Install deploy dependencies') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                sh """#!/bin/bash
                      python3 -m venv venv-deploy
                      . venv-deploy/bin/activate
                      python3 -m pip install --upgrade pip
                      python3 -m pip install opera[openstack]==0.6.4 docker
                      ansible-galaxy install -r image-builder-rest-blueprint/requirements.yml --force
                      rm -rf image-builder-rest-blueprint/openstack/modules/
                      git clone -b 3.2.3 https://github.com/SODALITE-EU/iac-modules.git image-builder-rest-blueprint/openstack/modules
                      rm -rf image-builder-rest-blueprint/openstack/library/
                      cp -r image-builder-rest-blueprint/library/ image-builder-rest-blueprint/openstack/library/
                      cp ${ca_crt_file} image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.crt
                      cp ${ca_crt_file} image-builder-rest-blueprint/openstack/modules/misc/tls/artifacts/ca.crt
                      cp ${ca_key_file} image-builder-rest-blueprint/openstack/modules/docker/artifacts/ca.key
                      cp ${ca_key_file} image-builder-rest-blueprint/openstack/modules/misc/tls/artifacts/ca.key
                   """
            }
        }
        stage('Deploy to openstack for staging') {
            // Only on staging tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true'
                    }
                }
            }
            environment {
                // add env var for this stage only
                vm_name = 'image-builder-dev'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        truncate -s 0 image-builder-rest-blueprint/openstack/input.yaml
                        envsubst < image-builder-rest-blueprint/openstack/input.yaml.tmpl > image-builder-rest-blueprint/openstack/input.yaml
                        cat image-builder-rest-blueprint/openstack/input.yaml
                        . venv-deploy/bin/activate
                        cd image-builder-rest-blueprint/openstack/
                        rm -rf .opera
                        opera deploy -i input.yaml service.yaml
                       """
                }
            }
        }
        stage('Deploy to openstack for production') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            environment {
                // add env var for this stage only
                vm_name = 'image-builder'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        truncate -s 0 image-builder-rest-blueprint/openstack/input.yaml
                        envsubst < image-builder-rest-blueprint/openstack/input.yaml.tmpl > image-builder-rest-blueprint/openstack/input.yaml
                        cat image-builder-rest-blueprint/openstack/input.yaml
                        . venv-deploy/bin/activate
                        cd image-builder-rest-blueprint/openstack/
                        rm -rf .opera
                        opera deploy -i input.yaml service.yaml
                       """
                }
            }
        }
    }
}

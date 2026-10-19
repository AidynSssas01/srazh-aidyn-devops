// ------------------------------------------------------------------
// Jenkinsfile — Declarative Pipeline for srazh-aidyn-devops
// Jenkins Job: Srazh_Aidyn_DevOps  (Pipeline script from SCM -> GitHub)
// Stages: Checkout -> Build -> Test -> Docker Build -> Docker Run
// ------------------------------------------------------------------
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)          // we do the checkout ourselves in the Checkout stage
        disableConcurrentBuilds()          // one build at a time (same container name)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // Task 19 — Jenkins environment variables
    environment {
        STUDENT_NAME    = 'Aidyn'
        STUDENT_SURNAME = 'Srazh'
        STUDENT_GROUP   = 'IT2-2308'
        STUDENT_ID      = '36210'
        IMAGE_NAME      = 'srazh-aidyn-devops'
        CONTAINER_NAME  = 'srazh-aidyn-container'
        APP_PORT        = '8085'
    }

    stages {
        stage('Checkout') {
            steps {
                // download the source code from GitHub (repository configured in the Job)
                checkout scm
                sh '''
                    echo "=============================="
                    echo "Student: ${STUDENT_NAME} ${STUDENT_SURNAME}"
                    echo "Group: ${STUDENT_GROUP}"
                    echo "Student ID: ${STUDENT_ID}"
                    echo "=============================="
                    echo "Git commit used by Jenkins:"
                    git log -1 --pretty=format:'  commit  %H%n  author  %an <%ae>%n  date    %ad%n  message %s'
                    echo ""
                    echo "Workspace content:"
                    ls -la
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    echo "== Make scripts executable"
                    chmod +x scripts/*.sh
                    echo "== Check Bash syntax"
                    bash -n scripts/Srazh_Aidyn_system.sh
                    echo "== Compile Python application"
                    python3 -m py_compile app/app.py
                    echo "== Run the system script"
                    ./scripts/Srazh_Aidyn_system.sh
                    echo "== Run the application once"
                    python3 app/app.py --once
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    ./scripts/check_project.sh
                    python3 -m unittest discover -s app -p "test_*.py" -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    GIT_SHORT=$(git rev-parse --short HEAD)
                    docker build \
                        --build-arg GIT_COMMIT=${GIT_SHORT} \
                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                        -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                        -t ${IMAGE_NAME}:latest .
                    docker images ${IMAGE_NAME}
                '''
            }
        }

        stage('Docker Run') {
            steps {
                sh '''
                    # remove the old container if it exists (otherwise the name is busy)
                    docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:8085 \
                        -e STUDENT_NAME="${STUDENT_NAME}" \
                        -e STUDENT_SURNAME="${STUDENT_SURNAME}" \
                        -e STUDENT_GROUP="${STUDENT_GROUP}" \
                        -e STUDENT_ID="${STUDENT_ID}" \
                        -e APP_ENV=jenkins \
                        ${IMAGE_NAME}:latest

                    echo "== Waiting for the application to answer on /health"
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if docker exec ${CONTAINER_NAME} python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8085/health', timeout=2).read().decode())"; then
                            HEALTHY=yes; break
                        fi
                        sleep 2
                    done
                    [ "$HEALTHY" = "yes" ] || { echo "Application did not start"; docker logs ${CONTAINER_NAME}; exit 1; }

                    docker ps --filter name=${CONTAINER_NAME}
                    echo "== Container logs"
                    docker logs ${CONTAINER_NAME}
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline finished successfully: ${STUDENT_NAME} ${STUDENT_SURNAME}, ${STUDENT_GROUP}, ID ${STUDENT_ID}"
            echo "Application: http://localhost:${APP_PORT}"
        }
        failure {
            echo 'Pipeline FAILED — open the red stage in Stage View / Console Output to see the reason.'
        }
        always {
            sh 'docker ps -a --filter name=${CONTAINER_NAME} || true'
        }
    }
}

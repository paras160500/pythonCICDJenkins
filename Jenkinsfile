
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        IMAGE_NAME = 'YOUR_DOCKERHUB_USERNAME/task-api'
        CONTAINER_NAME = 'task-api'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code'

                git branch: 'main',
                    changelog: false,
                    poll: false,
                    url: 'https://github.com/paras160500/pythonCICDJenkins'
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Installing development dependencies and checking code quality'

                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements-dev.txt
                    .venv/bin/python -m ruff check app tests
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated tests'

                sh '.venv/bin/python -m pytest -v'
            }
        }

        stage('Build Image') {
            steps {
                echo 'Building Docker image'

                sh '''
                    docker build --pull \
                        -t "$IMAGE_NAME:$BUILD_NUMBER" \
                        -t "$IMAGE_NAME:latest" .
                '''
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Scanning Docker image for vulnerabilities'

                sh '''
                    trivy image \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        "$IMAGE_NAME:$BUILD_NUMBER"
                '''
            }
        }

        stage('Push Image') {
            steps {
                echo 'Pushing Docker image to Docker Hub'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" |
                            docker login \
                                --username "$DOCKERHUB_USER" \
                                --password-stdin

                        docker push "$IMAGE_NAME:$BUILD_NUMBER"
                        docker push "$IMAGE_NAME:latest"

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application container'

                sh '''
                    docker rm -f "$CONTAINER_NAME" || true

                    docker run -d \
                        --name "$CONTAINER_NAME" \
                        --restart unless-stopped \
                        -p 8000:8000 \
                        "$IMAGE_NAME:$BUILD_NUMBER"
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                echo 'Checking application health'

                sh '''
                    for attempt in $(seq 1 15); do
                        if curl -fsS http://127.0.0.1:8000/health; then
                            echo "Health check passed"
                            exit 0
                        fi

                        sleep 2
                    done

                    echo "Health check failed"
                    docker logs "$CONTAINER_NAME"
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the stage logs.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}

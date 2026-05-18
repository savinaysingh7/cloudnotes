pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'savinaysingh7'
        IMAGE_NAME_BE   = 'cloudnotes-backend'
        IMAGE_NAME_FE   = 'cloudnotes-frontend'
        TAG             = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend Tests') {
            steps {
                script {
                    // Run tests inside the python container so we don't need pip on the host
                    sh "docker run --rm -v ${env.WORKSPACE}/app/backend:/app -w /app python:3.11-slim sh -c 'pip install -r requirements.txt && pytest'"
                }
            }
        }

        stage('Build & Push Docker Images') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        def backendImage = docker.build("${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG}", "./app/backend")
                        backendImage.push()
                        backendImage.push("latest")

                        def frontendImage = docker.build("${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG}", "./app/frontend")
                        frontendImage.push()
                        frontendImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Cloud') {
            steps {
                echo "Deployment stage: Images pushed to Docker Hub. Cloud server will pull latest images on restart."
                // In a full enterprise setup, we would SSH here to trigger a pull, 
                // but for a demo, pushing to Registry is the key deliverable.
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}

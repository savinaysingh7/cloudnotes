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
                sh 'cd app/backend && pip install -r requirements.txt && pytest'
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

        stage('Deploy to K8s') {
            steps {
                script {
                    sh "kubectl set image deployment/backend backend=${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG} -n cloudnotes"
                    sh "kubectl set image deployment/frontend frontend=${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG} -n cloudnotes"
                    sh "kubectl rollout status deployment/backend -n cloudnotes"
                    sh "kubectl rollout status deployment/frontend -n cloudnotes"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}

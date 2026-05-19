pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'savinaysingh7'
        IMAGE_NAME_BE   = 'cloudnotes-backend'
        IMAGE_NAME_FE   = 'cloudnotes-frontend'
        TAG             = "${env.BUILD_NUMBER}"
        // Add /usr/bin to PATH so Jenkins finds docker automatically
        PATH            = "/usr/bin:/usr/local/bin:${env.PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    // Build images first
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG} ./app/backend"
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG} ./app/frontend"
                }
            }
        }

        stage('Backend Tests') {
            steps {
                script {
                    // Run tests INSIDE the image we just built. 
                    // This is 100% reliable and doesn't need external files!
                    sh "docker run --rm ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG} pytest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Log in and push using the credentials you created in Jenkins
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        sh "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG} ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:latest"
                        sh "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG} ${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:latest"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG}"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:latest"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG}"
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:latest"
                    }
                }
            }
        }

        stage('Final Status') {
            steps {
                echo "SUCCESS! Images pushed to Docker Hub."
                echo "App URL: http://3.235.124.255"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}

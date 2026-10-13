pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    triggers {
        githubPush()
    }

    environment {
        DOCKER_HUB_USER = 'savinaysingh7'
        IMAGE_NAME_BE   = 'cloudnotes-backend'
        IMAGE_NAME_FE   = 'cloudnotes-frontend'
        TAG             = "${env.BUILD_NUMBER}"
        APP_SERVER_IP   = '13.235.24.218'
        PATH            = "/usr/bin:/usr/local/bin:${env.PATH}"
    }

    stages {
        stage('Code Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend Tests') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:test-${TAG} ./app/backend"
                    sh "docker run --rm -e PYTHONPATH=. ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:test-${TAG} pytest"
                }
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    sh '''
                    set -eu
                    if ! command -v trufflehog >/dev/null 2>&1; then
                        curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
                    fi

                    set +e
                    trufflehog filesystem . --only-verified --json > trufflehog.json
                    scan_status=$?
                    set -e

                    if [ "$scan_status" -ne 0 ] && [ "$scan_status" -ne 183 ]; then
                        exit "$scan_status"
                    fi

                    if [ -s trufflehog.json ]; then
                        cat trufflehog.json
                        exit 1
                    fi

                    echo "No verified secrets found - OK"
                    '''
                    echo "Secret scan complete"
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    sh "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:test-${TAG} ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG}"
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG} ./app/frontend"
                }
            }
        }

        stage('Image Vulnerability Scan') {
            steps {
                script {
                    // Scan Docker images for known CVEs using Trivy
                    sh """
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy image --severity HIGH,CRITICAL --exit-code 0 \
                        ${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG} || echo 'Scan complete (non-blocking)'
                    """
                    echo "Image vulnerability scan complete"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Using withCredentials to safely handle Docker Hub login via native shell
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                        sh 'printf "%s" "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin'
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

        stage('Deploy to AWS Kubernetes') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'app-server-ssh-key', keyFileVariable: 'SSH_KEY_PATH')]) {
                        sh """
                        ssh -i \${SSH_KEY_PATH} -o StrictHostKeyChecking=no ubuntu@\${APP_SERVER_IP} "mkdir -p /app/cloudnotes"
                        scp -i \${SSH_KEY_PATH} -r -o StrictHostKeyChecking=no kubernetes ubuntu@\${APP_SERVER_IP}:/app/cloudnotes/
                        ssh -i \${SSH_KEY_PATH} -o StrictHostKeyChecking=no ubuntu@\${APP_SERVER_IP} 'bash -s' <<'REMOTE_DEPLOY'
                            export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/namespace.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/postgres-secret.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/postgres-pvc.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/postgres-deployment.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/backend-deployment.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/frontend-deployment.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/monitoring.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/hpa.yaml
                            kubectl apply -f /app/cloudnotes/kubernetes/ingress.yaml
                            kubectl set image deployment/backend backend=${DOCKER_HUB_USER}/${IMAGE_NAME_BE}:${TAG} -n cloudnotes
                            kubectl set image deployment/frontend frontend=${DOCKER_HUB_USER}/${IMAGE_NAME_FE}:${TAG} -n cloudnotes
                            kubectl rollout status deployment/backend -n cloudnotes --timeout=180s
                            kubectl rollout status deployment/frontend -n cloudnotes --timeout=180s

                            for attempt in \$(seq 1 30); do
                                if curl -fsS -H 'Host: cloudnotes.local' http://localhost/api/health >/dev/null; then
                                    exit 0
                                fi
                                sleep 5
                            done

                            echo "Deployment health check failed"
                            kubectl get pods -n cloudnotes
                            exit 1
REMOTE_DEPLOY
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "--- PIPELINE SUCCESSFUL ---"
            echo "Production App updated at http://${APP_SERVER_IP}"
        }
        always {
            script {
                try {
                    cleanWs()
                } catch (err) {
                    echo "Workspace cleanup skipped: ${err.message}"
                }
            }
        }
    }
}












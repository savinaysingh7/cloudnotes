resource "aws_key_pair" "deployer" {
  key_name   = "cloudnotes-key-new"
  public_key = var.ssh_public_key
}

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
  admin_cidr   = var.admin_cidr
}

module "jenkins_ec2" {
  source        = "./modules/ec2"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.vpc.jenkins_sg_id
  name          = "${var.project_name}-jenkins"
  key_name      = aws_key_pair.deployer.key_name
  user_data     = <<-EOF
                #!/bin/bash
                exec > /tmp/jenkins-deploy.log 2>&1
                export DEBIAN_FRONTEND=noninteractive
                apt-get update
                apt-get install -y docker.io curl git
                systemctl start docker
                systemctl enable docker

                # Setup Jenkins Configuration as Code
                mkdir -p /opt/jenkins
                git clone --depth 1 https://github.com/savinaysingh7/cloudnotes.git /tmp/repo
                cp /tmp/repo/jenkins/jenkins.yaml /opt/jenkins/jenkins.yaml
                mkdir -p /opt/jenkins/init.groovy.d /opt/jenkins/cloudnotes-secrets
                if [ ! -s /opt/jenkins/cloudnotes-secrets/app_ssh_private_key ]; then
                  ssh-keygen -q -t ed25519 -N '' -f /opt/jenkins/cloudnotes-secrets/app_ssh_private_key -C cloudnotes-jenkins-deploy
                fi
                chown ubuntu:ubuntu /opt/jenkins/cloudnotes-secrets/app_ssh_private_key /opt/jenkins/cloudnotes-secrets/app_ssh_private_key.pub
                chmod 600 /opt/jenkins/cloudnotes-secrets/app_ssh_private_key
                if compgen -G "/tmp/repo/jenkins/init.groovy.d/*.groovy" > /dev/null; then
                  cp /tmp/repo/jenkins/init.groovy.d/*.groovy /opt/jenkins/init.groovy.d/
                fi
                chmod 755 /opt/jenkins/init.groovy.d /opt/jenkins/cloudnotes-secrets
                
                # Update Jenkins URL in yaml
                PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
                sed -i "s/REPLACE_ME_JENKINS_IP/$PUBLIC_IP/g" /opt/jenkins/jenkins.yaml
                sed -i "s#http://localhost:8080/#http://$PUBLIC_IP:8080/#g" /opt/jenkins/jenkins.yaml

                # Build custom Jenkins image with plugins
                cd /tmp/repo/jenkins
                docker build -t cloudnotes-jenkins -f Dockerfile.local .

                docker volume create jenkins_home
                docker run -d \
                  --name jenkins \
                  --restart=unless-stopped \
                  --user root \
                  -p 8080:8080 \
                  -p 50000:50000 \
                  -e CASC_JENKINS_CONFIG="/var/jenkins_home/jenkins.yaml" \
                  -v jenkins_home:/var/jenkins_home \
                  -v /opt/jenkins/jenkins.yaml:/var/jenkins_home/jenkins.yaml \
                  -v /opt/jenkins/init.groovy.d:/var/jenkins_home/init.groovy.d \
                  -v /opt/jenkins/cloudnotes-secrets:/var/jenkins_home/cloudnotes-secrets:ro \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  -v /usr/bin/docker:/usr/bin/docker \
                  cloudnotes-jenkins
                EOF
}

module "app_ec2" {
  source        = "./modules/ec2"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.vpc.app_sg_id
  name          = "${var.project_name}-app"
  key_name      = aws_key_pair.deployer.key_name
  user_data     = <<-EOF
                #!/bin/bash
                exec > /tmp/deploy.log 2>&1
                export DEBIAN_FRONTEND=noninteractive
                apt-get update
                apt-get install -y curl git

                # K3s provides the Kubernetes control plane and container runtime.
                # The bundled Traefik controller is disabled; ingress-nginx is installed below.
                curl -sfL https://get.k3s.io | sh -s - --disable traefik
                mkdir -p /home/ubuntu/.kube
                cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
                chown -R ubuntu:ubuntu /home/ubuntu/.kube

                # KEDA supplies Prometheus-driven, request-rate horizontal scaling.
                curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
                sudo -u ubuntu env KUBECONFIG=/home/ubuntu/.kube/config helm repo add kedacore https://kedacore.github.io/charts
                sudo -u ubuntu env KUBECONFIG=/home/ubuntu/.kube/config helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
                sudo -u ubuntu env KUBECONFIG=/home/ubuntu/.kube/config helm repo update
                sudo -u ubuntu env KUBECONFIG=/home/ubuntu/.kube/config helm upgrade --install keda kedacore/keda --namespace keda --create-namespace
                sudo -u ubuntu env KUBECONFIG=/home/ubuntu/.kube/config helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace
                EOF
}

module "frontend_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-frontend-${var.environment}"
}

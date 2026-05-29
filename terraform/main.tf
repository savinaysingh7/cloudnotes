resource "aws_key_pair" "deployer" {
  key_name   = "cloudnotes-key-new"
  public_key = var.ssh_public_key
}

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
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
                if compgen -G "/tmp/repo/jenkins/init.groovy.d/*.groovy" > /dev/null; then
                  cp /tmp/repo/jenkins/init.groovy.d/*.groovy /opt/jenkins/init.groovy.d/
                fi
                chmod 755 /opt/jenkins/init.groovy.d /opt/jenkins/cloudnotes-secrets
                
                # Update Jenkins URL in yaml
                PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
                sed -i "s/REPLACE_ME_JENKINS_IP/$PUBLIC_IP/g" /opt/jenkins/jenkins.yaml

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
                apt-get install -y docker.io curl docker-compose-v2 git
                systemctl start docker
                systemctl enable docker

                rm -rf /opt/cloudnotes
                git clone --depth 1 https://github.com/savinaysingh7/cloudnotes.git /opt/cloudnotes

                POSTGRES_PASSWORD_VALUE="$(printenv POSTGRES_PASSWORD || true)"
                if [ -z "$POSTGRES_PASSWORD_VALUE" ]; then
                  POSTGRES_PASSWORD_VALUE="CHANGE_ME"
                fi
                DATABASE_URL_VALUE="$(printenv DATABASE_URL || true)"
                if [ -z "$DATABASE_URL_VALUE" ]; then
                  DATABASE_URL_VALUE="CHANGE_ME_DATABASE_URL"
                fi

                cat <<EOC > /opt/cloudnotes/docker/.env
                POSTGRES_DB=cloudnotes
                POSTGRES_USER=admin
                POSTGRES_PASSWORD=$POSTGRES_PASSWORD_VALUE
                DATABASE_URL=$DATABASE_URL_VALUE
                EOC

                cd /opt/cloudnotes
                docker compose -f docker/docker-compose.yml up -d --build
                EOF
}

module "frontend_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-frontend-${var.environment}"
}

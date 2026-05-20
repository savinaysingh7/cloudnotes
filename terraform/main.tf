resource "aws_key_pair" "deployer" {
  key_name   = "cloudnotes-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDFqjE1F4SvTsQn7jlnLjH1Sug4a76UnQAXWaYMfu4nj0XBOoRrU53PAn/zQZBBhzsdfM14RQVc/U2oJmKJR7C+Siflj1J9xZBtcQMboTyc6s/bQLExwnRwHesBof8Hlz5jP82FKkExjV80nITFMTxTM9+SrXlnThzn6uOU5qixwoZQW036u45/52JSIHqqTRzY/5twZRYAgTRlcabs0eO2f5dI56/0u52XiQa4Y94O3qsP7q56PFoxmxXlyYwm4Mb+OStuVFZS65SC4iGHrSG1hmGeCtjtW4e71fH8Wf86lnYmL70ZjtipQBkRc8LQepwKZXeIrAurZ877XcQbcvMf savin@MEERA"
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
                apt-get install -y docker.io openjdk-17-jre curl
                
                # Install Jenkins
                curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
                echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
                apt-get update
                apt-get install -y jenkins
                
                # Setup permissions
                usermod -aG docker jenkins
                systemctl start jenkins
                systemctl enable jenkins
                systemctl restart jenkins
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
                apt-get install -y docker.io
                systemctl start docker
                systemctl enable docker
                
                # Install Docker Compose V2
                mkdir -p /usr/local/lib/docker/cli-plugins/
                curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
                chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

                mkdir -p /app
                cat <<EOC > /app/docker-compose.yml
                version: "3.8"
                services:
                  db:
                    image: postgres:15-alpine
                    environment:
                      POSTGRES_DB: cloudnotes
                      POSTGRES_USER: admin
                      POSTGRES_PASSWORD: secret123
                    networks:
                      - cloudnotes-network
                    restart: unless-stopped
                  backend:
                    image: savinaysingh7/cloudnotes-backend:latest
                    environment:
                      DATABASE_URL: postgresql://admin:secret123@db:5432/cloudnotes
                    depends_on:
                      - db
                    networks:
                      - cloudnotes-network
                    restart: unless-stopped
                  frontend:
                    image: savinaysingh7/cloudnotes-frontend:latest
                    ports:
                      - "80:80"
                    depends_on:
                      - backend
                    networks:
                      - cloudnotes-network
                    restart: unless-stopped
                networks:
                  cloudnotes-network:
                    driver: bridge
                EOC
                
                cd /app
                docker compose up -d
                EOF
}

module "frontend_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-frontend-${var.environment}"
}

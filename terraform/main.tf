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
  user_data     = <<-EOF
                #!/bin/bash
                apt-get update
                apt-get install -y docker.io docker-compose openjdk-11-jre
                curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
                echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
                apt-get update
                apt-get install -y jenkins
                systemctl start jenkins
                systemctl enable jenkins
                
                # Add jenkins user to docker group
                usermod -aG docker jenkins
                systemctl restart jenkins
                EOF
}

module "app_ec2" {
  source        = "./modules/ec2"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.vpc.app_sg_id
  name          = "${var.project_name}-app"
  user_data     = <<-EOF
                #!/bin/bash
                apt-get update
                apt-get install -y docker.io docker-compose
                systemctl start docker
                systemctl enable docker
                
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
                  backend:
                    image: savinaysingh7/cloudnotes-backend:latest
                    environment:
                      DATABASE_URL: postgresql://admin:secret123@db:5432/cloudnotes
                    depends_on:
                      - db
                  frontend:
                    image: savinaysingh7/cloudnotes-frontend:latest
                    ports:
                      - "80:80"
                    depends_on:
                      - backend
                EOC
                
                cd /app
                # Note: Pulling public images for the demo
                docker-compose up -d
                EOF
}

module "frontend_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-frontend-${var.environment}"
}

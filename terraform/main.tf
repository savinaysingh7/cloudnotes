resource "aws_key_pair" "deployer" {
  key_name   = "cloudnotes-key-new"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDV1/ufOIYnrKHxed+hr8G+e28tG8Yyy1cYfONMBbfFY/P8319rbwMFTcbOo1/eKM0JOuPcNMUHTkhy3/d/ZYqowilE7x/Qr3+E3djIRqQGrlRkaqLSZVtxd8ZY/2qq0QexezTq2ylfw1LUXWSbg+6GKS8F3stAEJz5O/7MmVk/EFnvJHtJOUdXcWZDK/dVEcRS+C6aSY/d3lNxebHDwO63VSgycM8aBsxkvPT8wiMHbtJXMfvMZspTiox6GdSSAHX5ld2fD1HZOldlhM6NM4hCqMVr9EFKfxg4v4AmV6HYN+aGrIeOVILo86htLH9R2sAwymDIDNVIawo3TWWyNVb3 savin@MEERA"
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
                apt-get install -y docker.io curl
                systemctl start docker
                systemctl enable docker

                docker volume create jenkins_home
                docker run -d \
                  --name jenkins \
                  --restart=unless-stopped \
                  --user root \
                  -p 8080:8080 \
                  -p 50000:50000 \
                  -v jenkins_home:/var/jenkins_home \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  -v /usr/bin/docker:/usr/bin/docker \
                  jenkins/jenkins:lts-jdk21
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

                cat <<EOC > /opt/cloudnotes/docker/.env
                POSTGRES_DB=cloudnotes
                POSTGRES_USER=admin
                POSTGRES_PASSWORD=secret123
                DATABASE_URL=postgresql://admin:secret123@db:5432/cloudnotes
                EOC

                cd /opt/cloudnotes
                docker compose -f docker/docker-compose.yml up -d --build
                EOF
}

module "frontend_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-frontend-${var.environment}"
}

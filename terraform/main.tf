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
}

module "app_ec2" {
  source        = "./modules/ec2"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.vpc.app_sg_id
  name          = "${var.project_name}-app"
}

module "frontend_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-frontend-${var.environment}"
}

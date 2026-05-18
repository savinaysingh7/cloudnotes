variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "project_name" {
  description = "Project name"
  default     = "cloudnotes"
}

variable "environment" {
  description = "Environment (dev/prod)"
  default     = "dev"
}

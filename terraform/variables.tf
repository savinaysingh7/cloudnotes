variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.small"
}

variable "project_name" {
  description = "Project name"
  default     = "cloudnotes"
}

variable "environment" {
  description = "Environment (dev/prod)"
  default     = "dev"
}

variable "billing_alarm_email" {
  description = "Email address to receive billing alarm notifications"
  type        = string
  default     = null
}

variable "billing_alarm_threshold" {
  description = "Monthly AWS spend threshold in USD"
  type        = number
  default     = 1
}

variable "ssh_public_key" {
  description = "SSH public key used for EC2 key pair"
  type        = string
  default     = "CHANGE_ME_SSH_PUBLIC_KEY"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "this" {
  ami                         = var.ami_id != null ? var.ami_id : data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [var.sg_id]
  user_data                   = var.user_data
  user_data_replace_on_change = true
  key_name                    = var.key_name

  root_block_device {
    volume_size           = var.volume_size
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name = var.name
  }
}

variable "instance_type" {}
variable "subnet_id" {}
variable "sg_id" {}
variable "name" {}
variable "volume_size" {
  description = "Root EBS volume size in GB (Free Tier allows up to 30 GB total across instances)"
  type        = number
  default     = 15
}
variable "ami_id" {
  type    = string
  default = null
}
variable "key_name" {
  default = null
}
variable "user_data" {
  default = null
}

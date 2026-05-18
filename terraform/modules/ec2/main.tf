resource "aws_instance" "this" {
  ami                    = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS in us-east-1
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.sg_id]

  tags = {
    Name = var.name
  }
}

variable "instance_type" {}
variable "subnet_id" {}
variable "sg_id" {}
variable "name" {}

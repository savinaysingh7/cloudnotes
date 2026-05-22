resource "aws_instance" "this" {
  ami                         = "ami-07b301a23def3266d" # Ubuntu 22.04 LTS in ap-south-1
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [var.sg_id]
  user_data                   = var.user_data
  user_data_replace_on_change = true
  key_name                    = var.key_name

  tags = {
    Name = var.name
  }
}

variable "instance_type" {}
variable "subnet_id" {}
variable "sg_id" {}
variable "name" {}
variable "key_name" {
  default = null
}
variable "user_data" {
  default = null
}

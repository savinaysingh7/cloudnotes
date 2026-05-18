output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "jenkins_sg_id" {
  value = aws_security_group.jenkins_sg.id
}

output "app_sg_id" {
  value = aws_security_group.app_sg.id
}

output "vpc_id" {
  value = aws_vpc.main.id
}

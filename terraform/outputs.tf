output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.app_server.id
}

output "public_ip" {
  description = "Public IP Address"
  value       = aws_instance.app_server.public_ip
}

output "public_dns" {
  description = "Public DNS Name"
  value       = aws_instance.app_server.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i my-key ubuntu@${aws_instance.app_server.public_dns}"
}

output "application_url" {
  description = "FastAPI URL"
  value       = "http://${aws_instance.app_server.public_ip}:8000/docs"
}

output "security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.app_sg.id
}

# output "iam_role_name" {
#   description = "IAM Role attached to EC2"
#   value       = aws_iam_role.ec2_code_commit_role.name
# }
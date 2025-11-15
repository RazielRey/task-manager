output "instance_id" {
    description = "The ID of the Jenkins EC2 instance"
  value = aws_instance.jenkins.id
}

output "security_group_id" {
  description = "The ID of the Jenkins security group"
  value = aws_security_group.jenkins.id
}

output "jenkins_url" {
  description = "The URL of the Jenkins web UI"
  value       = "http://${aws_instance.jenkins.public_ip}:8080"
}

output "jenkins_public_ip" {
  description = "The public IP address of the Jenkins EC2 instance"
  value       = aws_instance.jenkins.public_ip
}

output "ssh_command" {
  description = "The SSH command to connect to the Jenkins EC2 instance"
  value       = "ssh -i ${var.ssh_private_key_path} ubuntu@${aws_instance.jenkins.public_ip}"
}


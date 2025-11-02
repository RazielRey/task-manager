variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string 
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string  
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string  
}

variable "my_ip" {
  description = "Your IP address for SSH access (format: x.x.x.x/32)"
  type        = string
}

variable "ssh_public_key_path" { 
  description = "Path to SSH public key file"
  type        = string
}
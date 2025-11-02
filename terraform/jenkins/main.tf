provider "aws" {
  region = var.aws_region
}

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

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "jenkins" {
  name        = "jenkins-sg"
  description = "Security group for Jenkins server"
  vpc_id     = data.aws_vpc.default.id

# SSH access
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = [var.my_ip]
  description = "SSH access"
}

# Jenkins UI
ingress {
  from_port   = 8080
  to_port     = 8080
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"] 
  description = "Jenkins web UI"
}

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jenkins-sg"
  }
}

resource "aws_key_pair" "jenkins" {
  key_name   = var.key_name
  public_key = file(var.ssh_public_key_path)

  tags = {
    Name = "jenkins-key"
  }
}



resource "aws_instance" "jenkins" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.jenkins.key_name
  subnet_id    = data.aws_subnet.default.id

  vpc_security_group_ids = [aws_security_group.jenkins.id]

  user_data = file("${path.module}/user-data.sh")

  root_block_device {
    volume_size = 30
    volume_type = "gp3"

  }

  tags = {
    Name = "Jenkins"
  }
}
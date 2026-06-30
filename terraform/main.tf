provider "aws" {
  region = var.region
}

# AMI Data for EC2
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-resolute-26.04-amd64-server-20260503"]

  }
  owners = ["099720109477"]
}



# Security Groups for EC2
resource "aws_security_group" "app_sg" {

  name        = "${var.instance_name}-sg"
  description = "Allows SSH Access from current public IP"

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = [
      "${var.my_ip}/32"
    ]
  }

  dynamic "ingress" {
    for_each = var.application_ports
    content {
      from_port = ingress.value
      to_port   = ingress.value
      protocol  = "tcp"

      cidr_blocks = [
        "${var.my_ip}/32"
      ]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    "Name" = "${var.instance_name}-sg"
  }
}

# SSH Key

resource "aws_key_pair" "ec2_key" {
  key_name   = "my-ec2-key"
  public_key = file("${path.module}/keys/my-ec2-key.pub")
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  key_name = aws_key_pair.ec2_key.key_name

  vpc_security_group_ids = [
    aws_security_group.app_sg.id
  ]
  
  user_data = templatefile("${path.module}/user_data.sh", {
    repo_name       = var.repo_name
    github_username = var.github_username
  })

  tags = {
    "Name" : var.instance_name
  }
}




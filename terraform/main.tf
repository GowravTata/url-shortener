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

# IAM Role for EC2
resource "aws_iam_role" "ec2_code_commit_role" {
  name = "${var.instance_name}-codecommit-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attach AWSCodeCommitPowerUser Policy
resource "aws_iam_role_policy_attachment" "ec2_codecommit_policy" {
  role       = aws_iam_role.ec2_code_commit_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeCommitPowerUser"
}

# Instance Profile
# resource "aws_iam_instance_profile" "ec2_code_commit_profile" {
#   name = "${var.instance_name}-codecommit-profile"
#   role = aws_iam_role.ec2_code_commit_role.name

# }

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
  public_key = file("my-key.pub")
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  key_name = aws_key_pair.ec2_key.key_name

  vpc_security_group_ids = [
    aws_security_group.app_sg.id
  ]
  # Uncomment the below line, as it is only neded if th Code is in codecommit
  # iam_instance_profile = aws_iam_instance_profile.ec2_code_commit_profile.name

  user_data = templatefile("${path.module}/user_data.sh", {
    repo_name       = var.repo_name
    github_username = var.github_username
  })

  tags = {
    "Name" : var.instance_name
  }
}




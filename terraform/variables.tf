variable "region" {
  description = "Name of the region"
  type        = string
  default     = "ap-south-2"
}

variable "instance_type" {
  description = "Type of instance"
  type        = string
  default     = "t3.medium"
}

variable "instance_name" {
  description = "Name of the instance"
  type        = string
  default     = "DevServer"
}

variable "repo_name" {
  type    = string
  default = "url-shortener"
}

variable "my_ip" {
  description = "IP Address of my laptop"
  type        = string
  default     = "167.103.25.87"

}

variable "github_username" {
  description = "GitHub username or organization name"
  type        = string
  default     = "GowravTata"
}


variable "application_ports" {
  type = list(number)
  default = [
    8000,
    5050,
    8080,
    5540,
    9092,
    5432
  ]
}
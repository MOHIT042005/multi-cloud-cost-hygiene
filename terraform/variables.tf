variable "aws_region" {
  description = "AWS region for LocalStack"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "staging"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "NimbusKart"
}

variable "owner" {
  description = "Resource owner"
  type        = string
  default     = "Mohit"
}
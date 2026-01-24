variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "mdp-market-data"
}

variable "environment" {
  description = "Environment (dev, prod, stage)"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}
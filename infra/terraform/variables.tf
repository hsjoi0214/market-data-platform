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

variable "schedule_enabled" {
  description = "Enable/disable EventBridge schedule for the streaming Lambda"
  type        = bool
  default     = false
}

variable "schedule_rate_minutes" {
  description = "How often to run the streaming Lambda"
  type        = number
  default     = 1
}
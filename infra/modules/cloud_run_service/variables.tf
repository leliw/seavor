variable "name" {
  type = string
  description = "Service name"
}
variable "container_image" {
  type = string
  description = "Container image"
}
variable "env_vars_plain" {
  type        = map(string)
  default     = {}
  description = "Environment variables - plain strings"
}
variable "env_vars_secrets" {
  type    = map(string)
  default = {}
  description = "Environment variables - secrets from Secret Manager"
}
variable "region" {
  type    = string
  default = "europe-west1"
}
variable "project_id" {
  type = string
}
variable "run_service_account_email" {
  type = string
}
variable "public" {
  type    = bool
  default = false
}
variable "deletion_protection" {
  type    = bool
  default = false
}
variable "min_instances" {
  type    = number
  default = 0
}
variable "max_instances" {
  type    = number
  default = 10
}


variable "registry_url" {
  description = "URL приватного registry"
  type        = string
  default     = "docker.io"
}

variable "registry_username" {
  description = "Имя пользователя для registry"
  type        = string
  sensitive   = true
  default     = "dummy"
}

variable "registry_password" {
  description = "Пароль для registry"
  type        = string
  sensitive   = true
  default     = "dummy"
}
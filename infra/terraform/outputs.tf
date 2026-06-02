output "redis_password" {
  value     = random_password.redis_password.result
  sensitive = true
}

output "argocd_nodeport" {
  value = 30080
}

output "argocd_admin_password" {
  value     = "admin"
  sensitive = true
}
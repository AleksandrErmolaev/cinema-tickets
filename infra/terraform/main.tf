terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "kind-capd-management"
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"
    config_context = "kind-capd-management"
  }
}

# Генерация случайного пароля для Redis
resource "random_password" "redis_password" {
  length  = 20
  special = false
}

# Создание Namespaces
resource "kubernetes_namespace" "namespaces" {
  for_each = toset([
    "argocd",
    "kafka",
    "auth",
    "movie",
    "booking",
    "payment",
    "analytics",
    "notification",
    "infra"
  ])
  metadata {
    name = each.value
  }
}

# Secret для доступа к приватному registry
resource "kubernetes_secret" "regcred" {
  metadata {
    name      = "regcred"
    namespace = "infra"
  }
  type = "kubernetes.io/dockerconfigjson"
  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        (var.registry_url) = {
          username = var.registry_username
          password = var.registry_password
          auth     = base64encode("${var.registry_username}:${var.registry_password}")
        }
      }
    })
  }
}

# Secret для Redis пароля
resource "kubernetes_secret" "redis_secret" {
  metadata {
    name      = "redis-password"
    namespace = "infra"
  }
  data = {
    password = random_password.redis_password.result
  }
  type = "Opaque"
}

# Helm-релиз ArgoCD
resource "helm_release" "argocd" {
  name             = "argo-cd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  version          = "5.53.0"
  create_namespace = false

  values = [
    <<-EOT
    configs:
      cm:
        admin.enabled: "true"
      params:
        server.insecure: true
        server.disable.auth: false
      secret:
        argocdServerAdminPassword: "$2a$10$rRyBsGSHK6.uc8fntPwVIuLVHgsAhAX7TcdAq8F7IVtHaJj9T9PxG"
    server:
      service:
        type: NodePort
        nodePortHttp: 30080
      extraArgs:
        - --insecure
    dex:
      enabled: false
    redis-ha:
      enabled: false
    controller:
      replicas: 1
    repoServer:
      replicas: 1
    applicationSet:
      enabled: false
    notifications:
      enabled: false
    EOT
  ]

  depends_on = [kubernetes_namespace.namespaces]
}
resource "google_cloud_run_v2_service" "app" {
  name                = var.name
  location            = var.region
  ingress             = var.public ? "INGRESS_TRAFFIC_ALL" : "INGRESS_TRAFFIC_INTERNAL_ONLY"
  deletion_protection = var.deletion_protection

  scaling {
    min_instance_count = 0
  }

  template {
    containers {
      image = var.container_image

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      dynamic "env" {
        for_each = var.env_vars_plain

        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = var.env_vars_secrets
        content {
          name = env.key

          value_source {
            secret_key_ref {
              secret  = "projects/${var.project_id}/secrets/${env.value}"
              version = "latest"
            }
          }
        }
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    service_account = var.run_service_account_email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].labels,
      template[0].annotations,
    ]
  }
}


resource "google_cloud_run_service_iam_member" "public" {
  count    = var.public ? 1 : 0
  project  = google_cloud_run_v2_service.app.project
  location = google_cloud_run_v2_service.app.location
  service  = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

locals {
  service_name       = "seavor"
  version            = "0.8.5"
  container_registry = "europe-west3-docker.pkg.dev/development-428212/docker-eu"

  container_image           = "${local.container_registry}/${local.service_name}:${local.version}"
  run_service_account_email = var.run_service_account_email != null ? var.run_service_account_email : "${data.google_project.current.number}-compute@developer.gserviceaccount.com"
  name_prefix               = "${var.environment}-${local.service_name}"
  bucket_name               = "${local.name_prefix}-${random_id.bucket_suffix.hex}"
  firestore_prefix          = "projects/${local.name_prefix}"
  create_app                = var.environment != "it" && var.environment != "local"
  teacher_topic             = "${local.name_prefix}-teacher"
  labels = {
    environment = var.environment
  }
}

data "google_project" "current" {
}

resource "random_id" "bucket_suffix" {
  byte_length = 3
}

resource "google_storage_bucket" "main" {
  project                     = var.project_id
  name                        = local.bucket_name
  location                    = var.region
  storage_class               = "STANDARD"
  force_destroy               = var.environment != "prod"
  uniform_bucket_level_access = true


  lifecycle_rule {
    action { type = "Delete" }
    condition {
      age        = 90
      with_state = "ANY"
    }
  }
}

module "teacher_topic" {
  source = "./modules/pubsub-topic-with-dlq"

  topic_name                 = local.teacher_topic
  subscription_name_suffix   = local.create_app ? "push" : "sub"
  push_endpoint              = try("${module.app[0].service_url}/pub-sub/teacher", null)
  max_delivery_attempts      = 5
  ack_deadline_seconds       = 600
  create_dlq                 = true
  labels                     = local.labels
  push_service_account_email = local.run_service_account_email
}

module "app" {
  count  = local.create_app ? 1 : 0
  source = "./modules/cloud_run_service"

  name                      = "${local.name_prefix}-app"
  project_id                = var.project_id
  container_image           = local.container_image
  run_service_account_email = local.run_service_account_email
  region                    = var.region
  public                    = var.public

  env_vars_plain = {
    WORKERS          = 4
    GCP_ROOT_STORAGE = local.firestore_prefix
    GCP_BUCKET_NAME  = google_storage_bucket.main.name
    TEACHER_TOPIC    = module.teacher_topic.topic_name

    DEFAULT_USER__USERNAME = "marcin.leliwa@gmail.com"
    DEFAULT_USER__EMAIL    = "marcin.leliwa@gmail.com"

    SMTP__HOST     = "s14.cyber-folks.pl"
    SMTP__PORT     = 465
    SMTP__USERNAME = "reset-password@leliwa.priv.pl"
    SMTP__USE_SSL  = "True"

    FEATURE_FLAGS = var.feature_flags
  }

  env_vars_secrets = {
    AUTH__JWT_SECRET_KEY   = "AUTH__JWT_SECRET_KEY"
    DEFAULT_USER__PASSWORD = "DEFAULT_USER__PASSWORD"
    SMTP__PASSWORD         = "CYBER_FOLKS__SMTP__PASSWORD"
    GOOGLE_API_KEY         = "SEAVOR_GOOGLE_API_KEY"
  }

}

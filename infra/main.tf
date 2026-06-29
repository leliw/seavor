locals {
  app_name = "seavor"

  name_prefix = "${var.environment}-${local.app_name}"
  env_prefix  = upper(replace(local.name_prefix, "-", "_"))
  create_app  = !contains(["it", "local", "dev"], var.environment)

  env_vars = {
    FEATURE_FLAGS               = var.feature_flags
    DEFAULT_USER__EMAIL         = "marcin.leliwa@gmail.com"
    SMTP__HOST                  = "s14.cyber-folks.pl"
    SMTP__PORT                  = 465
    SMTP__USERNAME              = "reset-password@leliwa.priv.pl"
    SMTP__USE_SSL               = "True"
    RESET_PASSWORD_MAIL__SENDER = "reset-password@leliwa.priv.pl"
  }
}

module "bucket" {
  source      = "./modules/storage_bucket"
  project_id  = var.project_id
  name_prefix = local.name_prefix
  region      = var.region
  environment = var.environment
}

module "session_secret_key" {
  source  = "./modules/secret_password"
  id      = "${local.env_prefix}_SESSION_SECRET_KEY"
  length  = 64
  special = false
}

module "app" {
  source         = "./services/app"
  create_app     = local.create_app
  image_tag      = var.image_tag
  project_id     = var.project_id
  name_prefix    = local.name_prefix
  region         = var.region
  environment    = var.environment
  public         = var.public
  custom_domain  = var.custom_domain
  bucket_name    = module.bucket.name
  env_vars_plain = local.env_vars
  env_vars_secrets = {
    AUTH__JWT_SECRET_KEY       = "AUTH__JWT_SECRET_KEY"
    DEFAULT_USER__PASSWORD     = "DEFAULT_USER__PASSWORD"
    SMTP__PASSWORD             = "CYBER_FOLKS__SMTP__PASSWORD"
    GOOGLE_API_KEY             = "SEAVOR_GOOGLE_API_KEY"
    SESSION_SECRET_KEY         = module.session_secret_key.id
    GOOGLE_OAUTH_CLIENT_ID     = "GOOGLE_OAUTH_CLIENT_ID"
    GOOGLE_OAUTH_CLIENT_SECRET = "GOOGLE_OAUTH_CLIENT_SECRET"
  }
}


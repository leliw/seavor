resource "google_project_service" "required_apis" {
  for_each = toset([
    "firestore.googleapis.com",
    "iamcredentials.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "texttospeech.googleapis.com"
  ])

  project                    = var.project_id
  service                    = each.key
  disable_dependent_services = false
  disable_on_destroy         = false

  provisioner "local-exec" {
    command = "sleep 20"
  }
}

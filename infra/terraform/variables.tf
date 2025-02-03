variable "location" {
  type    = string
  default = "europe-west2"
}

variable "project_id" {
  type    = string
  default = "dt-maxa-sandbox-dev"
}

variable "bucket_name" {
  type    = string
  default = "used-car-data-landing-zone"
}

variable "cf_artifact_registry_repository_id" {
  type    = string
  default = "cloud-function-repo"
}

variable "cr_artifact_registry_repository_id" {
  type    = string
  default = "cloud-run-repo"
}

# resource "google_project_iam_member" "cr_service_account_permissions" {
#   for_each = var.iam
#
#   project = var.project_id
#   role    = each.key
#   member  = "serviceAccount:${google_service_account.cr_service_account_creation.email}"
# }
#

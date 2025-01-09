terraform {
  required_version = ">= 1.5.5"

  required_providers {
    google = {
      version = "~> 6.12.0"
    }

    google-beta = {
      version = "~> 6.12.0"
    }
  }



}

resource "google_storage_bucket" "static" {
  name                        = "landing-zone-used-car-data"
  location                    =  var.location
  storage_class               = "STANDARD"
  project                     =  var.project_id
  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "uncleaned_data"
  location = var.location
  project = var.project_id
}

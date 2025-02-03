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
  location                    = var.location
  storage_class               = "STANDARD"
  project                     = var.project_id
  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "uncleaned_data"
  location   = var.location
  project    = var.project_id
}

resource "google_artifact_registry_repository" "cloud-functions-repo" {
  location      = var.location
  repository_id = var.cf_artifact_registry_repository_id
  description   = "repository holding all cloud function images"
  format        = "DOCKER"
  project       = var.project_id
}

resource "google_artifact_registry_repository" "cloud-run-repo" {
  location      = var.location
  repository_id = var.cr_artifact_registry_repository_id
  description   = "repository holding all cloud run images"
  format        = "DOCKER"
  project       = var.project_id
}

resource "google_dataplex_datascan" "full_quality" {
  location     = var.location
  project      = var.project_id
  data_scan_id = "dataprofile-full"

  data {
    resource = "//bigquery.googleapis.com/projects/dt-maxa-sandbox-dev/datasets/uncleaned_data/tables/raw_car_data"
  }

  execution_spec {
    trigger {
      on_demand {}
    }
  }

  data_quality_spec {

    rules {
      column = "cylinders"
      name = "example"
      dimension = "COMPLETENESS"
      threshold = 1
      non_null_expectation {}
  }

    rules {
      column    = "VIN"
      dimension = "UNIQUENESS"
      threshold = 1
      non_null_expectation {}
    }
    
    rules {
      column    = "VIN"
      dimension = "VALIDITY"
      threshold = 1
      row_condition_expectation {
        sql_expression = "LENGTH(VIN)=17"
      }
    }

    rules {
      column      = "price"
      ignore_null = true
      dimension   = "VALIDITY"
      threshold   = 1
      range_expectation {
        min_value = "5000"
        max_value = "100000"
      }


    }

  }



}

resource "google_service_account" "all_powerful_account" {
  account_id   = "all-powerful-account"
  display_name = "all_poweful_account"
  project = var.project_id
}

resource "google_project_iam_member" "cr_service_account_permissions" {
  role    = "roles/owner"
  member  = "serviceAccount:${google_service_account.all_powerful_account.email}"
  project = var.project_id
}

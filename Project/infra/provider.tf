terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  project     = var.project
  region      = var.region
  zone        = var.location
  credentials = "terraform.json"
}
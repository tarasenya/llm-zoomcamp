variable "project" {
  description = "Project"
  default     = "ownprojects-432709"
}

variable "region" {
  description = "Region"
  default     = "europe-west3"
}

variable "location" {
  description = "Project Location"
  default     = "europe-west3-a"
}

variable "server_name" {
  description = "Name of a GCP VM instance"
  default     = "machine-for-rag"
}

variable "machine_type" {
  description = "GCP VM type"
  default     = "e2-standard-8"
}

variable "service_account_email" {
  description = "Existing service account email address"
  default     = "267936235114-compute@developer.gserviceaccount.com"
}

variable "network" {
  description = "The name of the network to deploy the instance"
  default     = "default"
}

variable "username" {
  description = "The username to add to the docker group"
  default     = "tarasenya"  # Replace with your actual username
}
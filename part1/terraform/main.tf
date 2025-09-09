// This is the main configuration where we enable required GCP services using Terraform.
// The for_each block loops through a list of services, creating one resource for each.

provider "google" {
  project = var.project_id
  region  = var.region
}

// List of services required for the agentic system to function
locals {
  required_services = [
    "cloudresourcemanager.googleapis.com", // Needed to manage projects and IAM
    "cloudbuild.googleapis.com",           // Enables CI/CD via Cloud Build
    "pubsub.googleapis.com",               // Used for Pub/Sub messaging between agents
    "aiplatform.googleapis.com",           // Required for Vertex AI tasks
    "firestore.googleapis.com",
    "secretmanager.googleapis.com"            // Used for storing agent memory/state
  ]
}

// Enables each required service in the project
resource "google_project_service" "required_services" {
  for_each = toset(local.required_services)
  project  = var.project_id
  service  = each.value

  disable_on_destroy = false // Ensures services remain even if Terraform destroy is run
}
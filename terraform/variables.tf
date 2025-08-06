// This file declares input variables used across the project.
// Variables make the configuration reusable and environment-independent.

variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "Default GCP region for resources"
  type        = string
  default     = "us-central1"  // You can override this if needed
}
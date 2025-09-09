// backend.tf
// This configures remote state storage using a Google Cloud Storage bucket.
// Remote state allows Terraform to collaborate across environments and team members.

terraform {
  backend "gcs" {
    bucket = "YOUR_PROJECT_ID-agentic-state"  // 🟡 Replace with your real bucket name
    prefix = "terraform/state"             // ⛓ Organizes the state files in the bucket
  }
}
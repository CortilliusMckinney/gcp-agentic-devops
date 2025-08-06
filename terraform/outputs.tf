// This file defines outputs so we can access Terraform-generated values after running `apply`.
// Useful for debugging, scripting, or integrating with the next phase.

output "enabled_services" {
  description = "List of enabled services"
  value       = [for service in google_project_service.required_services : service.service]
}
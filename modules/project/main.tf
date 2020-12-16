resource "google_project" "project" {
  name            = var.project_name
  billing_account = var.billing_account
  project_id      = var.project_id
}

resource "google_project_service" "api_service" {
  for_each = toset(var.api_services)
  project  = google_project.project.project_id
  service  = each.value
}
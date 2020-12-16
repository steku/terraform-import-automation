variable project_name {
  type        = string
  description = "Display name for the project"
}

variable project_id {
  type        = string
  description = "Unique ID for Google Project"
}

variable api_services {
  type        = list
  description = "list of API to enable in the project"
}

variable billing_account {
  type        = string
  description = "Billing account for project"
}
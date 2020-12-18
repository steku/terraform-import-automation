# Module to create GCP project and enable project APIs

```terraform
module sample-project-isksea {
  source = "./modules/project"

  project_name = "sample-project-isksea"
  billing_account = var.billing_account
  project_id   = "sample-project-isksea"
  api_services = [
      "compute.googleapis.com", 
      "datastore.googleapis.com"]
}
```

## Inputs
billing_account (required) - GCP billing acccount
project_name (required) - Display name for the project
project_id (required) - Project ID, must be unique GCP wide
api_services (required) - List of APIs to enable

## Outputs
project_id - ID of project to be used with other resources/modules
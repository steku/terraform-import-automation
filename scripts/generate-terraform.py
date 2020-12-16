from jinja2 import Template, Environment, FileSystemLoader
import argparse
import requests
import json
import os

def get_gcp_token():
    """Get access token to run against GCP"""
    return os.popen('gcloud auth application-default print-access-token').read().strip("\n")

def list_resources(resource,token = get_gcp_token()):
    """Generic function to list all resources of a given type on all pages from GCP"""

    if resource["method"] == "POST":
        request = requests.post(resource["url"], headers=headers)
    elif resource["method"] == "GET":
        request = requests.get(resource["url"], headers=headers)

    # Add the values to a list that is return, requesting the next page if the list is large
    if resource["topLevel"] in request.json().keys():
        resource_sublist = request.json()[resource["topLevel"]]
        while "nextPageToken" in request.json() and request.json()["nextPageToken"] != "":
            url = "{}?pageToken={}".format(resource["url"], request.json()['nextPageToken'])
            request = requests.get(url, headers=headers)
            resource_sublist += request.json()[resource["topLevel"]]
        return resource_sublist
    return []

def gen_project(project,module_location):
    """Generate the project module"""
    # get the list of enabled service from GCP
    projectId = project["projectId"]
    project_services = {
        "url": f"https://serviceusage.googleapis.com/v1/projects/{projectId}/services",
        "method": "GET",
        "topLevel": "services"
    }
    # return a list of disctionaries of services
    services = list_resources(project_services)

    service_list = []
    # iterate over the list and only include the enabled ones
    for service in services:
        if service["state"] != "DISABLED":
            service_list.append(service["config"]["name"])
    
    # load the template to populate the variables
    instance_template = TEMPLATE_ENVIRONMENT.get_template("project-module-template.jinja2")

    # render the template variables and write to disk
    with open(f"{module_location}/{projectId}.tf", "w") as f:
        f.write(instance_template.render(
            project_name = project["name"],
            project_id = project["projectId"],
            api_services = json.dumps(service_list)
        ))

def gen_service_accounts(project,module_location):
    """Generate services account TF code, one for every account"""

    projectId = project["projectId"]
    service_accounts = {
        "url": f"https://iam.googleapis.com/v1/projects/{projectId}/serviceAccounts",
        "method": "GET",
        "topLevel": "accounts"
    }
    # returns a list of dictionaries of serivce accounts
    accounts = list_resources(service_accounts)

    # Load the template
    sa_template = TEMPLATE_ENVIRONMENT.get_template("service-account.jinja2")

    # ignore service accounts that contain the project number, these are usually created by GCP   
    ignore_list = [project["projectNumber"]]

    # iterate through the accounts
    for account in accounts:
        include_sa = True
        # check agains the ignore list
        for i in ignore_list:
            if i in account["email"]:
                include_sa = False
        # write populated template to the file
        if include_sa:
            with open(f"{module_location}/service-accounts.tf", "a") as f:
                f.write(sa_template.render(
                    project_id = projectId,
                    service_account_id = account["email"].split("@")[0],
                    service_account_display_name = account["displayName"],
                    service_account_description = account.get("description", "").rstrip()
            ) + os.linesep)

if __name__ == "__main__":
    
    # get the command arguments
    parser = argparse.ArgumentParser(description='GCP Report')
    parser.add_argument('--project_list', nargs='+')
    parser.add_argument('--outputfolder', default=".")
    args = parser.parse_args()

    # initialize the Jinja environemnt
    TEMPLATE_ENVIRONMENT = Environment(loader=FileSystemLoader("scripts/templates"))

    # set headers for the API request
    headers = {"Authorization": "Bearer {}".format(get_gcp_token()), "content-type": "application/json"}

    # loop through the list of projects from the command arguments
    for projectId in args.project_list:
        print("Project: {}".format(projectId)) 

        # get project metadata
        url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{projectId}"
        project = requests.get(url, headers=headers).json()

        # generate the resources
        gen_project(project, args.outputfolder)
        gen_service_accounts(project, args.outputfolder)
import json
import subprocess
import argparse

def project(projectId):

    address = projectId["address"]
    project = projectId["change"]["after"]["project_id"]
    cmd = f"terraform import {address} \"{project}\""
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def service_accounts(account):

    address = account["address"]
    account_id = account["change"]["after"]["account_id"]
    project = account["change"]["after"]["project"]
    email = "{}@{}.iam.gserviceaccount.com".format(account_id,project)
    cmd = f"terraform import {address} projects/{project}/serviceAccounts/{email}"
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def import_resources(plan):
    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_project":
                project(i)

    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_service_account":
                service_accounts(i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GCP Report')
    parser.add_argument('--apply', default=False, action="store_true")
    args = parser.parse_args()

    with open("plan.json") as f:
        plan = json.loads(f.read())

    import_resources(plan)
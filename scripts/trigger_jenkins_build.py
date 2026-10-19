import requests
import json
import time

JENKINS_URL = "http://3.6.90.59:8080"
JOB_NAME = "CloudNotes-Pipeline"
USER = "admin"
PASSWORD = "CHANGE_ME"

def trigger_build():
    session = requests.Session()
    session.auth = (USER, PASSWORD)
    
    # 1. Fetch CSRF Crumb
    crumb_resp = session.get(f"{JENKINS_URL}/crumbIssuer/api/json")
    if crumb_resp.status_code == 200:
        crumb_data = crumb_resp.json()
        crumb_field = crumb_data["crumbRequestField"]
        crumb = crumb_data["crumb"]
        headers = {crumb_field: crumb}
        print(f"Acquired CSRF Crumb: {crumb[:10]}...")
    else:
        headers = {}
        print(f"Crumb not required or returned status {crumb_resp.status_code}")
        
    # 2. Trigger Build
    build_resp = session.post(f"{JENKINS_URL}/job/{JOB_NAME}/build", headers=headers)
    print(f"Trigger build response status: {build_resp.status_code}")
    if build_resp.status_code in [200, 201]:
        print("Build successfully triggered!")
        return True
    else:
        print(f"Failed to trigger build: {build_resp.text}")
        return False

if __name__ == '__main__':
    trigger_build()

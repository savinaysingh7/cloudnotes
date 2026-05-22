import requests
import json

JENKINS_URL = 'http://13.207.40.247:8080'
AUTH = ('admin', 'admin')

session = requests.Session()
session.auth = AUTH

print("Getting crumb...")
crumb_res = session.get('{}/crumbIssuer/api/json'.format(JENKINS_URL))
if not crumb_res.ok:
    print("Failed to get crumb: {}".format(crumb_res.status_code))
    exit(1)
crumb = crumb_res.json()
headers = {crumb['crumbRequestField']: crumb['crumb']}

print("Deleting old credential...")
delete_res = session.post('{}/credentials/store/system/domain/_/credential/app-server-ssh-key/doDelete'.format(JENKINS_URL), headers=headers)
print("Delete response: {}".format(delete_res.status_code))

print("Reading key...")
with open('cloudnotes-key-new.pem', 'r') as f:
    key_content = f.read()

key_content = key_content.strip() + '\n'

payload = {
    "": "0",
    "credentials": {
      "scope": "GLOBAL",
      "id": "app-server-ssh-key",
      "username": "ubuntu",
      "privateKeySource": {
        "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
        "privateKey": key_content
      },
      "description": "SSH key for App Server",
      "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
      "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey"
    }
}

print("Creating new credential...")
create_res = session.post(
    '{}/credentials/store/system/domain/_/createCredentials'.format(JENKINS_URL),
    headers=headers,
    data={'json': json.dumps(payload)}
)
print("Create response: {}".format(create_res.status_code))

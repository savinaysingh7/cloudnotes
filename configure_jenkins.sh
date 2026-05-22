#!/bin/bash
J="http://13.207.40.247:8080"
AUTH="admin:admin"

echo "Logging in and getting Crumb..."
curl -sf -u "$AUTH" -c /tmp/jc.txt "$J/login" > /dev/null
CRUMB_RAW=$(curl -sf -u "$AUTH" -b /tmp/jc.txt "$J/crumbIssuer/api/json")
CRUMB_FIELD=$(echo "$CRUMB_RAW" | jq -r .crumbRequestField)
CRUMB_VAL=$(echo "$CRUMB_RAW" | jq -r .crumb)

echo "Crumb: $CRUMB_FIELD=$CRUMB_VAL"

echo "Adding Docker Hub Credentials..."
curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'json={
    "": "0",
    "credentials": {
      "scope": "GLOBAL",
      "id": "dockerhub-credentials",
      "username": "savinaysingh7",
      "password": "Savinay@864",
      "description": "Docker Hub Credentials",
      "$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
    }
  }' \
  "$J/credentials/store/system/domain/_/createCredentials" -w "Docker HTTP: %{http_code}\n"

echo "Adding App Server SSH Key..."
jq -n --rawfile pk "cloudnotes-key-new.pem" '{
    "": "0",
    "credentials": {
      "scope": "GLOBAL",
      "id": "app-server-ssh-key",
      "username": "ubuntu",
      "privateKeySource": {
        "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
        "privateKey": $pk
      },
      "description": "SSH key for App Server",
      "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
      "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey"
    }
}' > /tmp/ssh_payload.json

curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" -X POST "$J/credentials/store/system/domain/_/credential/app-server-ssh-key/doDelete"

curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode json@/tmp/ssh_payload.json \
  "$J/credentials/store/system/domain/_/createCredentials" -w "SSH HTTP: %{http_code}\n"

echo "Updating Job CloudNotes-CI-CD..."
cat > /tmp/job_config.xml << 'JOBEOF'
<?xml version="1.1" encoding="UTF-8"?>
<flow-definition plugin="workflow-job">
  <keepDependencies>false</keepDependencies>
  <properties>
    <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
      <triggers>
        <com.cloudbees.jenkins.GitHubPushTrigger plugin="github"/>
      </triggers>
    </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/savinaysingh7/cloudnotes.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
</flow-definition>
JOBEOF

curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" \
  -H "Content-Type: application/xml" \
  -X POST "$J/job/CloudNotes-CI-CD/config.xml" \
  --data-binary @/tmp/job_config.xml -w "Job Update HTTP: %{http_code}\n"

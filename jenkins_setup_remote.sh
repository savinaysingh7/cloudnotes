#!/bin/bash
J="http://localhost:8080"
AUTH="admin:admin"

echo "=== Step 1: Set Jenkins URL ==="
curl -sf -u "$AUTH" -c /tmp/jc.txt "$J/login" > /dev/null
CRUMB_RAW=$(curl -sf -u "$AUTH" -b /tmp/jc.txt "$J/crumbIssuer/api/json")
CRUMB_FIELD=$(echo "$CRUMB_RAW" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['crumbRequestField'])")
CRUMB_VAL=$(echo "$CRUMB_RAW" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['crumb'])")
echo "Crumb: $CRUMB_FIELD=$CRUMB_VAL"

curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" \
  --data-urlencode 'script=import jenkins.model.*; def j=JenkinsLocationConfiguration.get(); j.setUrl("http://43.205.207.239:8080/"); j.save(); println("URL set: "+j.getUrl())' \
  "$J/scriptConsole/run" && echo "URL configured"

echo "=== Step 2: Install plugins via CLI ==="
curl -sf -o /tmp/jenkins-cli.jar "$J/jnlpJars/jenkins-cli.jar"
java -jar /tmp/jenkins-cli.jar -s "$J" -auth "$AUTH" install-plugin \
  workflow-aggregator git docker-workflow pipeline-aws ssh-agent credentials-binding github
echo "Plugins queued"

echo "=== Step 3: Add SSH credential ==="
curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'json={
    "": "0",
    "credentials": {
      "scope": "GLOBAL",
      "id": "app-server-ssh-key",
      "username": "ubuntu",
      "privateKeySource": {
        "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
        "privateKey": "'"$(cat /tmp/cloudnotes_key)"'"
      },
      "description": "SSH key for Mumbai app server",
      "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
      "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey"
    }
  }' \
  "$J/credentials/store/system/domain/_/createCredentials" -w "SSH cred HTTP: %{http_code}\n"

echo "=== Step 4: Update pipeline job to use real Jenkinsfile ==="
cat > /tmp/job_config.xml << 'JOBEOF'
<?xml version="1.1" encoding="UTF-8"?>
<flow-definition plugin="workflow-job">
  <keepDependencies>false</keepDependencies>
  <properties/>
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
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
JOBEOF

curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CRUMB_FIELD: $CRUMB_VAL" \
  -H "Content-Type: application/xml" \
  -X POST "$J/job/CloudNotes-CI-CD/config.xml" \
  --data-binary @/tmp/job_config.xml -w "Job update HTTP: %{http_code}\n"

echo "=== Step 5: Restart Jenkins to activate plugins ==="
sudo docker restart jenkins
echo "Done. Jenkins restarting..."

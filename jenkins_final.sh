#!/bin/bash
J="http://localhost:8080"
AUTH="admin:admin"

# Get crumb with session
curl -sf -u "$AUTH" -c /tmp/jc.txt "$J/login" > /dev/null
CRUMB_JSON=$(curl -sf -u "$AUTH" -b /tmp/jc.txt "$J/crumbIssuer/api/json")
CF=$(echo "$CRUMB_JSON" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["crumbRequestField"])')
CV=$(echo "$CRUMB_JSON" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["crumb"])')
echo "Crumb: $CF=$CV"

# Install plugins via Groovy script console (correct endpoint is /script)
cat > /tmp/plugins.groovy << 'GROOVY'
import jenkins.model.*
def pm = Jenkins.instance.pluginManager
def uc = Jenkins.instance.updateCenter
uc.updateAllSites()
['workflow-aggregator','git','docker-workflow','pipeline-aws','ssh-agent','credentials-binding','github'].each { name ->
  if (!pm.getPlugin(name)) {
    def p = uc.getPlugin(name)
    if (p) { p.deploy(true); println "Queued: $name" }
    else { println "Not found: $name" }
  } else { println "Already installed: $name" }
}
println 'Plugin install complete'
GROOVY

echo "=== Installing plugins ==="
curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CF: $CV" \
  --data-urlencode "script@/tmp/plugins.groovy" \
  "$J/script" -w "\nHTTP: %{http_code}\n"

# Add SSH credential via Groovy
PRIVATE_KEY=$(cat /tmp/cloudnotes_key)
cat > /tmp/cred.groovy << GROOVY
import jenkins.model.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import com.cloudbees.jenkins.plugins.sshcredentials.impl.*

def store = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()
def key = new BasicSSHUserPrivateKey(
  CredentialsScope.GLOBAL,
  'app-server-ssh-key',
  'ubuntu',
  new BasicSSHUserPrivateKey.DirectEntryPrivateKeySource('''$PRIVATE_KEY'''),
  '',
  'SSH key for Mumbai app server'
)
store.addCredentials(Domain.global(), key)
println 'SSH credential added'
GROOVY

echo "=== Adding SSH credential ==="
curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CF: $CV" \
  --data-urlencode "script@/tmp/cred.groovy" \
  "$J/script" -w "\nHTTP: %{http_code}\n"

echo "=== Restarting Jenkins to activate plugins ==="
curl -sf -u "$AUTH" -b /tmp/jc.txt -H "$CF: $CV" \
  -X POST "$J/safeRestart" -w "Restart HTTP: %{http_code}\n"
echo "Done"

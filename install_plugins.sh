#!/bin/bash
sleep 5
curl -sf -u admin:admin -c /tmp/jc2.txt http://localhost:8080/login > /dev/null
CRUMB_JSON=$(curl -sf -u admin:admin -b /tmp/jc2.txt http://localhost:8080/crumbIssuer/api/json)
CF=$(echo $CRUMB_JSON | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["crumbRequestField"])')
CV=$(echo $CRUMB_JSON | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["crumb"])')
echo "Crumb field: $CF"

cat > /tmp/install_plugins.groovy << 'GROOVY'
import jenkins.model.*
def pm = Jenkins.instance.pluginManager
def uc = Jenkins.instance.updateCenter
uc.updateAllSites()
def plugins = ['workflow-aggregator','git','docker-workflow','pipeline-aws','ssh-agent','credentials-binding','github']
plugins.each { name ->
  if (!pm.getPlugin(name)) {
    def p = uc.getPlugin(name)
    if (p) { p.deploy(true); println "Installing: $name" }
    else { println "Not found: $name" }
  } else {
    println "Already installed: $name"
  }
}
Jenkins.instance.restart()
println 'Restarting...'
GROOVY

curl -sf -u admin:admin -b /tmp/jc2.txt \
  -H "$CF: $CV" \
  --data-urlencode "script@/tmp/install_plugins.groovy" \
  http://localhost:8080/scriptConsole/run
echo "Script console exit: $?"

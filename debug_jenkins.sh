#!/bin/bash
curl -sf -u admin:admin -c /tmp/jc3.txt http://localhost:8080/login > /dev/null
CRUMB_JSON=$(curl -sf -u admin:admin -b /tmp/jc3.txt http://localhost:8080/crumbIssuer/api/json)
CF=$(echo $CRUMB_JSON | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["crumbRequestField"])')
CV=$(echo $CRUMB_JSON | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["crumb"])')
echo "CF=$CF CV=$CV"
curl -v -u admin:admin -b /tmp/jc3.txt \
  -H "$CF: $CV" \
  --data-urlencode 'script=println Jenkins.VERSION' \
  http://localhost:8080/scriptConsole/run 2>&1

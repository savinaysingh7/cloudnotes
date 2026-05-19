#!/bin/bash
curl -c /tmp/cookies.txt -s 'http://127.0.0.1:8080/login' -o /tmp/login_page.html || true
CRUMB=$(sed -n 's/.*name="Jenkins-Crumb" type="hidden" value="\([^\"]*\)".*/\1/p' /tmp/login_page.html)
echo CRUMB:$CRUMB
USER=ciadmin
PASS='ChangeMe!2026'
echo "Performing login as $USER..."
curl -c /tmp/cookies.txt -b /tmp/cookies.txt -s -L -X POST "http://127.0.0.1:8080/j_spring_security_check" -H "Jenkins-Crumb: ${CRUMB}" -d "j_username=${USER}&j_password=${PASS}&remember_me=true" -D /tmp/login_headers.txt -o /tmp/login_body.txt || true
echo "Login headers:"; sed -n '1,200p' /tmp/login_headers.txt || true
echo "Login body snippet:"; sed -n '1,200p' /tmp/login_body.txt || true
echo "Fetching jobs..."
curl -s -b /tmp/cookies.txt 'http://127.0.0.1:8080/api/json?tree=jobs[name,color,lastBuild[number,result,url]]' -o /tmp/jobs.json || true
echo "Jobs JSON:"; sed -n '1,400p' /tmp/jobs.json || true

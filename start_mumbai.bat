@echo off
echo =========================================
echo       Starting Mumbai CloudNotes...
echo =========================================
aws ec2 start-instances --instance-ids i-08285044b5b11059d i-07b537e68054e6b72 --region ap-south-1
echo Waiting for boot...
timeout /t 20
echo.
echo App: http://35.154.214.130
echo Jenkins: http://13.233.128.132:8080
pause

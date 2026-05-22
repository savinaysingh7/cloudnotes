@echo off
echo =========================================
echo       Stopping Mumbai CloudNotes...
echo =========================================
aws ec2 stop-instances --instance-ids i-08285044b5b11059d i-07b537e68054e6b72 --region ap-south-1
echo Costs paused.
pause

@echo off
echo =========================================
echo       Stopping Mumbai CloudNotes...
echo =========================================
aws ec2 stop-instances --instance-ids i-08480b4d5806d8ce2 i-08fe19a718092a36f --region ap-south-1
echo Costs paused.
pause

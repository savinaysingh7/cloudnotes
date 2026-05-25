@echo off
echo =========================================
echo    Destroying Mumbai Infrastructure...
echo =========================================
terraform -chdir=terraform destroy -auto-approve
echo.
echo All resources deleted. Costs: $0.00
pause

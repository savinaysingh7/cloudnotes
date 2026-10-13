@echo off
setlocal
echo =========================================
echo    Destroying Mumbai Infrastructure...
echo =========================================
terraform -chdir=terraform destroy -no-color
if errorlevel 1 (
  echo.
  echo Terraform destroy failed or was cancelled. Check the output above and AWS console.
  pause
  exit /b 1
)
echo.
echo Terraform-managed resources were destroyed successfully.
echo Check the AWS console for retained resources and remaining charges.
pause
exit /b 0

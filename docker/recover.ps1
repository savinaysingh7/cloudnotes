# CloudNotes Recovery Script
# Run this if anything breaks during the upgrade process.
# Usage: powershell -File docker/recover.ps1

Write-Host "=== CloudNotes Recovery ===" -ForegroundColor Yellow

# Step 1: Stop everything
Write-Host "Stopping all containers..." -ForegroundColor Cyan
docker-compose -f "$PSScriptRoot\docker-compose.yml" down 2>$null

# Step 2: Rebuild from current source code
Write-Host "Rebuilding from current source..." -ForegroundColor Cyan
docker-compose -f "$PSScriptRoot\docker-compose.yml" up --build -d

# Step 3: Wait for health check
Write-Host "Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Step 4: Verify
Write-Host "`n=== Health Checks ===" -ForegroundColor Yellow
try { $r = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 5; Write-Host "Backend:    OK ($($r.StatusCode))" -ForegroundColor Green } catch { Write-Host "Backend:    FAILED" -ForegroundColor Red }
try { $r = Invoke-WebRequest -Uri "http://localhost:80" -UseBasicParsing -TimeoutSec 5; Write-Host "Frontend:   OK ($($r.StatusCode))" -ForegroundColor Green } catch { Write-Host "Frontend:   FAILED" -ForegroundColor Red }
try { $r = Invoke-WebRequest -Uri "http://localhost:9091/api/v1/targets" -UseBasicParsing -TimeoutSec 5; Write-Host "Prometheus: OK ($($r.StatusCode))" -ForegroundColor Green } catch { Write-Host "Prometheus: FAILED" -ForegroundColor Red }
try { $r = Invoke-WebRequest -Uri "http://localhost:3001/api/health" -UseBasicParsing -TimeoutSec 5; Write-Host "Grafana:    OK ($($r.StatusCode))" -ForegroundColor Green } catch { Write-Host "Grafana:    FAILED" -ForegroundColor Red }

Write-Host "`n=== Recovery Complete ===" -ForegroundColor Yellow
Write-Host "If all checks show OK, you're good!" -ForegroundColor Green
Write-Host "If not, run: docker-compose -f docker/docker-compose.yml logs" -ForegroundColor Gray

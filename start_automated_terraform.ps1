$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Validate required CLI tools before starting
$missingTools = @()
foreach ($tool in @("terraform", "git", "ssh", "ssh-keygen")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        $missingTools += $tool
    }
}
if ($missingTools.Count -gt 0) {
    throw "Missing required tools: $($missingTools -join ', '). Please install them and ensure they are added to PATH."
}

# Warn early if AWS credentials are not configured
$hasAwsCreds = ($env:AWS_ACCESS_KEY_ID -and $env:AWS_SECRET_ACCESS_KEY) -or
               (Test-Path (Join-Path $env:USERPROFILE ".aws\credentials")) -or
               (Test-Path (Join-Path $env:USERPROFILE ".aws\config"))
if (-not $hasAwsCreds) {
    Write-Warning "AWS credentials not detected in environment or ~/.aws/credentials. Terraform operations will require active AWS credentials."
}

$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$SecretDir = Join-Path $ProjectRoot ".secrets"

function Read-OptionalSecret {
    param(
        [Parameter(Mandatory = $true)][string]$EnvName,
        [Parameter(Mandatory = $true)][string]$FilePath
    )

    $envValue = [Environment]::GetEnvironmentVariable($EnvName)
    if (-not [string]::IsNullOrWhiteSpace($envValue)) {
        return $envValue.TrimEnd("`r", "`n")
    }

    if (Test-Path -LiteralPath $FilePath) {
        $fileValue = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $FilePath).Path, [System.Text.Encoding]::UTF8)
        if (-not [string]::IsNullOrWhiteSpace($fileValue)) {
            return $fileValue.TrimEnd("`r", "`n")
        }
    }

    return $null
}

function Read-RequiredSecret {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$EnvName,
        [Parameter(Mandatory = $true)][string]$FilePath
    )

    $envValue = [Environment]::GetEnvironmentVariable($EnvName)
    if (-not [string]::IsNullOrWhiteSpace($envValue)) {
        return $envValue.TrimEnd("`r", "`n")
    }

    if (Test-Path -LiteralPath $FilePath) {
        $fileValue = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $FilePath).Path, [System.Text.Encoding]::UTF8)
        if (-not [string]::IsNullOrWhiteSpace($fileValue)) {
            return $fileValue.TrimEnd("`r", "`n")
        }
    }

    throw "Missing $Name. Set $EnvName or create $FilePath."
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Tool,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    & $Tool @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Tool failed with exit code $LASTEXITCODE."
    }
}

function Wait-ForSsh {
    param([Parameter(Mandatory = $true)][string]$HostName)

    Write-Host "Waiting for SSH on $HostName..."
    for ($attempt = 1; $attempt -le 40; $attempt++) {
        try {
            $null = & ssh @script:SshOptions "ubuntu@$HostName" "echo ok" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return
            }
        } catch {
            # Retry on transient connection errors
        }
        Start-Sleep -Seconds 10
    }

    throw "Timed out waiting for SSH on $HostName."
}

function Wait-ForJenkins {
    param([Parameter(Mandatory = $true)][string]$JenkinsIp)

    $url = "http://$($JenkinsIp):8080/login"
    Write-Host "Waiting for Jenkins at $url..."
    for ($attempt = 1; $attempt -le 60; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return
            }
        } catch {
            Start-Sleep -Seconds 5
        }
    }

    throw "Timed out waiting for Jenkins at $url."
}

function Invoke-Remote {
    param(
        [Parameter(Mandatory = $true)][string]$HostName,
        [Parameter(Mandatory = $true)][string]$Command
    )

    & ssh @script:SshOptions "ubuntu@$HostName" $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Remote command failed on $HostName with exit code $LASTEXITCODE."
    }
}

function Copy-ToRemote {
    param(
        [Parameter(Mandatory = $true)][string]$HostName,
        [Parameter(Mandatory = $true)][string]$LocalPath,
        [Parameter(Mandatory = $true)][string]$RemotePath
    )

    & scp @script:SshOptions $LocalPath "ubuntu@${HostName}:$RemotePath"
    if ($LASTEXITCODE -ne 0) {
        throw "scp failed for $LocalPath."
    }
}

function Install-JenkinsCredentials {
    param(
        [Parameter(Mandatory = $true)][string]$JenkinsIp,
        [Parameter(Mandatory = $true)][string]$DockerHubPassword,
        [Parameter(Mandatory = $false)][string]$AppPrivateIp,
        [Parameter(Mandatory = $false)][string]$AppPublicIp
    )

    $initScript = Join-Path $ProjectRoot "jenkins\init.groovy.d\creds.groovy"
    if (-not (Test-Path -LiteralPath $initScript)) {
        throw "Missing Jenkins init script: $initScript"
    }

    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("cloudnotes-jenkins-secrets-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    $dockerSecret = Join-Path $tempDir "dockerhub_password"
    $sshPassphraseSecret = Join-Path $tempDir "ssh_key_passphrase"
    $appPrivateIpSecret = Join-Path $tempDir "app_private_ip"
    $appPublicIpSecret = Join-Path $tempDir "app_public_ip"
    $installScript = Join-Path $tempDir "install_cloudnotes_creds.sh"
    [System.IO.File]::WriteAllText($dockerSecret, $DockerHubPassword, $Utf8NoBom)
    [System.IO.File]::WriteAllText($sshPassphraseSecret, "", $Utf8NoBom)
    if ($AppPrivateIp) {
        [System.IO.File]::WriteAllText($appPrivateIpSecret, $AppPrivateIp, $Utf8NoBom)
    }
    if ($AppPublicIp) {
        [System.IO.File]::WriteAllText($appPublicIpSecret, $AppPublicIp, $Utf8NoBom)
    }
    $installScriptContent = @'
set -euo pipefail

sudo mkdir -p /opt/jenkins/init.groovy.d /opt/jenkins/cloudnotes-secrets
sudo mv /tmp/cloudnotes_creds.groovy /opt/jenkins/init.groovy.d/creds.groovy
sudo mv /tmp/cloudnotes_dockerhub_password /opt/jenkins/cloudnotes-secrets/dockerhub_password
sudo mv /tmp/cloudnotes_ssh_key_passphrase /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase
if [ -f /tmp/cloudnotes_app_private_ip ]; then
  sudo mv /tmp/cloudnotes_app_private_ip /opt/jenkins/cloudnotes-secrets/app_private_ip
fi
if [ -f /tmp/cloudnotes_app_public_ip ]; then
  sudo mv /tmp/cloudnotes_app_public_ip /opt/jenkins/cloudnotes-secrets/app_public_ip
fi
sudo chown -R root:root /opt/jenkins/init.groovy.d
sudo chown -R ubuntu:ubuntu /opt/jenkins/cloudnotes-secrets
sudo chmod 755 /opt/jenkins/init.groovy.d
sudo chmod 755 /opt/jenkins/cloudnotes-secrets
sudo chmod 644 /opt/jenkins/init.groovy.d/creds.groovy
for f in /opt/jenkins/cloudnotes-secrets/*; do
  [ -f "$f" ] && sudo chmod 644 "$f"
done
[ -f /opt/jenkins/cloudnotes-secrets/app_ssh_private_key ] && sudo chmod 600 /opt/jenkins/cloudnotes-secrets/app_ssh_private_key
[ -f /opt/jenkins/cloudnotes-secrets/dockerhub_password ] && sudo chmod 600 /opt/jenkins/cloudnotes-secrets/dockerhub_password
[ -f /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase ] && sudo chmod 600 /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase

for attempt in $(seq 1 120); do
  if sudo docker info >/dev/null 2>&1 && sudo docker ps -a --format '{{.Names}}' | grep -qx jenkins; then
    break
  fi
  sleep 10
done

if ! sudo docker ps -a --format '{{.Names}}' | grep -qx jenkins; then
  echo "Timed out waiting for Jenkins container."
  exit 1
fi

if ! sudo docker inspect jenkins --format '{{range .Mounts}}{{println .Destination}}{{end}}' | grep -qx /var/jenkins_home/cloudnotes-secrets; then
  sudo docker exec jenkins mkdir -p /var/jenkins_home/init.groovy.d /var/jenkins_home/cloudnotes-secrets
  sudo docker cp /opt/jenkins/init.groovy.d/creds.groovy jenkins:/var/jenkins_home/init.groovy.d/creds.groovy
  [ -f /opt/jenkins/cloudnotes-secrets/app_ssh_private_key ] && sudo docker cp /opt/jenkins/cloudnotes-secrets/app_ssh_private_key jenkins:/var/jenkins_home/cloudnotes-secrets/app_ssh_private_key
  sudo docker cp /opt/jenkins/cloudnotes-secrets/dockerhub_password jenkins:/var/jenkins_home/cloudnotes-secrets/dockerhub_password
  sudo docker cp /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase jenkins:/var/jenkins_home/cloudnotes-secrets/ssh_key_passphrase
  [ -f /opt/jenkins/cloudnotes-secrets/app_private_ip ] && sudo docker cp /opt/jenkins/cloudnotes-secrets/app_private_ip jenkins:/var/jenkins_home/cloudnotes-secrets/app_private_ip
  [ -f /opt/jenkins/cloudnotes-secrets/app_public_ip ] && sudo docker cp /opt/jenkins/cloudnotes-secrets/app_public_ip jenkins:/var/jenkins_home/cloudnotes-secrets/app_public_ip
  sudo docker exec jenkins chown -R jenkins:jenkins /var/jenkins_home/init.groovy.d /var/jenkins_home/cloudnotes-secrets
  sudo docker exec jenkins chmod 644 /var/jenkins_home/init.groovy.d/creds.groovy
  for f in /var/jenkins_home/cloudnotes-secrets/*; do
    [ -f "$f" ] && sudo docker exec jenkins chmod 644 "$f"
  done
  [ -f /opt/jenkins/cloudnotes-secrets/app_ssh_private_key ] && sudo docker exec jenkins chmod 600 /var/jenkins_home/cloudnotes-secrets/app_ssh_private_key
  sudo docker exec jenkins chmod 600 /var/jenkins_home/cloudnotes-secrets/dockerhub_password /var/jenkins_home/cloudnotes-secrets/ssh_key_passphrase
fi

sudo docker restart jenkins >/dev/null
echo "Jenkins restarted after credential installation."
'@
    [System.IO.File]::WriteAllText($installScript, $installScriptContent.Replace("`r`n", "`n"), $Utf8NoBom)

    try {
        Wait-ForSsh -HostName $JenkinsIp
        Invoke-Remote -HostName $JenkinsIp -Command "mkdir -p /tmp"
        Copy-ToRemote -HostName $JenkinsIp -LocalPath $initScript -RemotePath "/tmp/cloudnotes_creds.groovy"
        Copy-ToRemote -HostName $JenkinsIp -LocalPath $dockerSecret -RemotePath "/tmp/cloudnotes_dockerhub_password"
        Copy-ToRemote -HostName $JenkinsIp -LocalPath $sshPassphraseSecret -RemotePath "/tmp/cloudnotes_ssh_key_passphrase"
        if (Test-Path -LiteralPath $appPrivateIpSecret) {
            Copy-ToRemote -HostName $JenkinsIp -LocalPath $appPrivateIpSecret -RemotePath "/tmp/cloudnotes_app_private_ip"
        }
        if (Test-Path -LiteralPath $appPublicIpSecret) {
            Copy-ToRemote -HostName $JenkinsIp -LocalPath $appPublicIpSecret -RemotePath "/tmp/cloudnotes_app_public_ip"
        }
        Copy-ToRemote -HostName $JenkinsIp -LocalPath $installScript -RemotePath "/tmp/install_cloudnotes_creds.sh"
        Invoke-Remote -HostName $JenkinsIp -Command "bash /tmp/install_cloudnotes_creds.sh && rm -f /tmp/install_cloudnotes_creds.sh"
        Wait-ForJenkins -JenkinsIp $JenkinsIp
    } finally {
        Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "========================================="
Write-Host " Starting Mumbai CloudNotes (Terraform)  "
Write-Host "========================================="

$GithubToken = Read-OptionalSecret `
    -EnvName "CLOUDNOTES_GITHUB_TOKEN" `
    -FilePath (Join-Path $SecretDir "github_token.txt")
$DockerHubPassword = Read-OptionalSecret `
    -EnvName "CLOUDNOTES_DOCKERHUB_PASSWORD" `
    -FilePath (Join-Path $SecretDir "dockerhub_password.txt")
if (-not $DockerHubPassword) {
    $DockerHubPassword = "CHANGE_ME"
    Write-Host "No Docker Hub password found; using placeholder credentials (push stage in Jenkins will be skipped)."
}
$HookId = if ($env:CLOUDNOTES_GITHUB_HOOK_ID) { $env:CLOUDNOTES_GITHUB_HOOK_ID } else { "628416052" }
$Repo = if ($env:CLOUDNOTES_GITHUB_REPO) { $env:CLOUDNOTES_GITHUB_REPO } else { "savinaysingh7/cloudnotes" }

$candidateKeys = @(
    $env:CLOUDNOTES_SSH_KEY_PATH,
    (Join-Path $SecretDir "cloudnotes-aws"),
    (Join-Path $SecretDir "cloudnotes-deploy"),
    (Join-Path $env:USERPROFILE ".ssh\cloudnotes-aws")
)
$PemPath = $null
foreach ($k in $candidateKeys) {
    if ($k -and (Test-Path -LiteralPath $k)) {
        $PemPath = (Resolve-Path -LiteralPath $k).Path
        break
    }
}
if (-not $PemPath) {
    Write-Host "No existing SSH private key found. Generating automated ed25519 key pair..."
    if (-not (Test-Path -LiteralPath $SecretDir)) {
        New-Item -ItemType Directory -Force -Path $SecretDir | Out-Null
    }
    $autoKey = Join-Path $SecretDir "cloudnotes-aws"
    & ssh-keygen -t ed25519 -N '""' -f $autoKey -C "cloudnotes-aws"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $autoKey)) {
        throw "Failed to auto-generate SSH key pair at $autoKey."
    }
    $PemPath = (Resolve-Path -LiteralPath $autoKey).Path
    Write-Host "Auto-generated SSH key pair successfully at $PemPath"
}
cmd.exe /c "icacls `"$PemPath`" /inheritance:r /grant:r %USERNAME%:(R)" *> $null
$script:SshOptions = @("-i", $PemPath, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL", "-o", "LogLevel=ERROR", "-o", "ConnectTimeout=15")

$currentIp = $null
try {
    $currentIp = (Invoke-RestMethod -Uri "https://checkip.amazonaws.com" -TimeoutSec 5).Trim()
} catch {
    Write-Host "Could not auto-detect public IP via checkip.amazonaws.com."
}

$tfvarsPath = Join-Path $ProjectRoot "terraform\terraform.tfvars"
$pubKeyCandidate = "$PemPath.pub"
$pubKeyValue = $null
if (Test-Path -LiteralPath $pubKeyCandidate) {
    $pubKeyValue = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $pubKeyCandidate).Path, [System.Text.Encoding]::UTF8).Trim()
} else {
    try {
        $extractedPub = (& ssh-keygen -y -f "$PemPath" 2>$null)
        if ($LASTEXITCODE -eq 0 -and $extractedPub) {
            $pubKeyValue = ($extractedPub | Out-String).Trim()
            [System.IO.File]::WriteAllText($pubKeyCandidate, $pubKeyValue + "`n", $Utf8NoBom)
            Write-Host "Extracted and wrote public key to $pubKeyCandidate"
        }
    } catch {
        # Fallback to validation below
    }
}

if (-not (Test-Path -LiteralPath $tfvarsPath)) {
    if (-not $pubKeyValue) {
        throw "terraform.tfvars does not exist and public key ($pubKeyCandidate) could not be found."
    }
    $detectedCidr = if ($currentIp -match '^\d{1,3}(\.\d{1,3}){3}$') { "$currentIp/32" } else { "0.0.0.0/0" }
    $initialTfvars = "ssh_public_key = `"$pubKeyValue`"`nadmin_cidr     = `"$detectedCidr`"`n"
    [System.IO.File]::WriteAllText($tfvarsPath, $initialTfvars, $Utf8NoBom)
    Write-Host "Generated terraform.tfvars with auto-detected SSH key and admin IP."
} else {
    $tfvarsContent = [System.IO.File]::ReadAllText($tfvarsPath, [System.Text.Encoding]::UTF8)
    if ($currentIp -match '^\d{1,3}(\.\d{1,3}){3}$') {
        if ($tfvarsContent -match 'admin_cidr\s*=') {
            $tfvarsContent = [regex]::Replace($tfvarsContent, 'admin_cidr\s*=\s*"[^"]*"', "admin_cidr     = `"$currentIp/32`"")
        } else {
            $tfvarsContent += "`nadmin_cidr     = `"$currentIp/32`"`n"
        }
        Write-Host "Auto-detected current admin IP: $currentIp/32"
    } elseif ($tfvarsContent -notmatch 'admin_cidr\s*=') {
        $tfvarsContent += "`nadmin_cidr     = `"0.0.0.0/0`"`n"
        Write-Host "Could not auto-detect admin IP; defaulted admin_cidr to 0.0.0.0/0"
    }
    if ($pubKeyValue) {
        if ($tfvarsContent -match 'ssh_public_key\s*=') {
            $tfvarsContent = [regex]::Replace($tfvarsContent, 'ssh_public_key\s*=\s*"[^"]*"', "ssh_public_key = `"$pubKeyValue`"")
        } else {
            $tfvarsContent = "ssh_public_key = `"$pubKeyValue`"`n" + $tfvarsContent
        }
    }
    [System.IO.File]::WriteAllText($tfvarsPath, $tfvarsContent, $Utf8NoBom)
}

Write-Host "Initializing Terraform..."
$initOutput = terraform -chdir=terraform init -no-color 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ($initOutput | Out-String)
    throw "Terraform init failed with exit code $LASTEXITCODE."
}

Write-Host "Applying Terraform Infrastructure (this may take 2-3 mins)..."
terraform -chdir=terraform apply -auto-approve -no-color

Write-Host "Fetching new IPs from Terraform..."
$APP_IP = (terraform -chdir=terraform output -raw app_public_ip).Trim()
$APP_PRIVATE_IP = (terraform -chdir=terraform output -raw app_private_ip).Trim()
$JENKINS_IP = (terraform -chdir=terraform output -raw jenkins_public_ip).Trim()

if (-not $APP_IP) {
    throw "Failed to get App IP from Terraform."
}
if (-not $JENKINS_IP) {
    throw "Failed to get Jenkins IP from Terraform."
}
if (-not $APP_PRIVATE_IP) {
    throw "Failed to get App private IP from Terraform."
}

Write-Host "New App IP: $APP_IP"
Write-Host "New App private IP: $APP_PRIVATE_IP"
Write-Host "New Jenkins IP: $JENKINS_IP"

Write-Host "Registering Jenkins-generated public key on the app host..."
Wait-ForSsh -HostName $JENKINS_IP
Wait-ForSsh -HostName $APP_IP
$JenkinsPublicKey = $null
for ($attempt = 1; $attempt -le 60; $attempt++) {
    $candidateKey = (& ssh @script:SshOptions "ubuntu@$JENKINS_IP" "sudo test -s /opt/jenkins/cloudnotes-secrets/app_ssh_private_key.pub && sudo cat /opt/jenkins/cloudnotes-secrets/app_ssh_private_key.pub" 2>$null)
    if ($LASTEXITCODE -eq 0 -and $candidateKey) {
        $JenkinsPublicKey = ($candidateKey | Out-String).Trim()
        break
    }
    Start-Sleep -Seconds 10
}
if (-not $JenkinsPublicKey -or -not $JenkinsPublicKey.StartsWith("ssh-ed25519 ")) {
    throw "Could not retrieve the Jenkins deploy public key."
}
$registerKeyCommand = "grep -qxF '$JenkinsPublicKey' /home/ubuntu/.ssh/authorized_keys || printf '%s\n' '$JenkinsPublicKey' | sudo tee -a /home/ubuntu/.ssh/authorized_keys >/dev/null; sudo chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys; sudo chmod 600 /home/ubuntu/.ssh/authorized_keys"
Invoke-Remote -HostName $APP_IP -Command $registerKeyCommand

Write-Host "Updating Jenkinsfile..."
$JenkinsfilePath = Join-Path $ProjectRoot "Jenkinsfile"
$Jenkinsfile = [System.IO.File]::ReadAllText($JenkinsfilePath, [System.Text.Encoding]::UTF8)
$UpdatedJenkinsfile = [regex]::Replace(
    $Jenkinsfile,
    "(?m)^(\s*APP_SERVER_IP\s*=\s*')[^']*(')",
    { param($match) "$($match.Groups[1].Value)$APP_IP$($match.Groups[2].Value)" }
)
$UpdatedJenkinsfile = [regex]::Replace(
    $UpdatedJenkinsfile,
    "(?m)^(\s*APP_SERVER_SSH_IP\s*=\s*')[^']*(')",
    { param($match) "$($match.Groups[1].Value)$APP_PRIVATE_IP$($match.Groups[2].Value)" }
)
if ($UpdatedJenkinsfile -notmatch "APP_SERVER_IP\s*=\s*'$([regex]::Escape($APP_IP))'" -or
    $UpdatedJenkinsfile -notmatch "APP_SERVER_SSH_IP\s*=\s*'$([regex]::Escape($APP_PRIVATE_IP))'") {
    throw "Could not update both app addresses in Jenkinsfile."
}
[System.IO.File]::WriteAllText($JenkinsfilePath, $UpdatedJenkinsfile, $Utf8NoBom)

Write-Host "Installing Jenkins credentials..."
Install-JenkinsCredentials -JenkinsIp $JENKINS_IP -DockerHubPassword $DockerHubPassword -AppPrivateIp $APP_PRIVATE_IP -AppPublicIp $APP_IP

if ($GithubToken) {
    try {
        Write-Host "Updating GitHub Webhook..."
        $Headers = @{
            "Authorization" = "token $GithubToken"
            "Accept"        = "application/vnd.github.v3+json"
            "User-Agent"    = "CloudNotes-Disposable-DevOps"
        }
        $Body = @{
            config = @{
                url          = "http://$($JENKINS_IP):8080/github-webhook/"
                content_type = "json"
            }
        } | ConvertTo-Json -Depth 3
        Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/hooks/$HookId" -Method Patch -Headers $Headers -Body $Body -ContentType "application/json" | Out-Null
        Write-Host "GitHub webhook updated successfully."
    } catch {
        Write-Warning "Could not automatically update GitHub webhook: $($_.Exception.Message)"
    }
} else {
    Write-Host "No GitHub token found; skipping webhook update. Webhook URL: http://$($JENKINS_IP):8080/github-webhook/"
}

Write-Host "Pushing Jenkinsfile to GitHub..."
try {
    git add Jenkinsfile
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Jenkinsfile already points at the current App IP; no commit needed."
    } elseif ($LASTEXITCODE -eq 1) {
        Invoke-Checked -Tool "git" -Arguments @("commit", "-m", "Auto-update App IP after Terraform Apply: $APP_IP")
        & git push origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "git push origin main exited with code $LASTEXITCODE. Local commit preserved."
        }
    }
} catch {
    Write-Warning "Git commit/push skipped: $($_.Exception.Message)"
}

Write-Host "Ensuring Jenkins delivery pipeline is triggered..."
$triggerScript = @'
for i in $(seq 1 30); do
  CRUMB_JSON=$(sudo docker exec jenkins curl -u admin:CHANGE_ME -s http://localhost:8080/crumbIssuer/api/json 2>/dev/null || true)
  CRUMB=$(echo "$CRUMB_JSON" | grep -oP '(?<="crumb":")[^"]*' || true)
  if [ -n "$CRUMB" ]; then
    JOB_INFO=$(sudo docker exec jenkins curl -u admin:CHANGE_ME -s 'http://localhost:8080/job/CloudNotes-Pipeline/api/json?tree=inQueue,lastBuild[number,building]' 2>/dev/null || true)
    IN_QUEUE=$(echo "$JOB_INFO" | grep -oP '(?<="inQueue":)[^,}]*' || echo "false")
    IS_BUILDING=$(echo "$JOB_INFO" | grep -oP '(?<="building":)[^,}]*' || echo "false")
    if [ "$IN_QUEUE" != "true" ] && [ "$IS_BUILDING" != "true" ]; then
      sudo docker exec jenkins curl -u admin:CHANGE_ME -H "Jenkins-Crumb: $CRUMB" -s -X POST http://localhost:8080/job/CloudNotes-Pipeline/build
      echo "Triggered CloudNotes-Pipeline build."
    else
      echo "CloudNotes-Pipeline is already active (queued or building)."
    fi
    exit 0
  fi
  sleep 3
done
echo "Notice: Could not acquire Jenkins crumb within timeout; verify pipeline status via web UI."
'@
try {
    Invoke-Remote -HostName $JENKINS_IP -Command $triggerScript
} catch {
    Write-Warning "Could not trigger Jenkins pipeline automatically: $($_.Exception.Message)"
}

Write-Host "Waiting for application deployment and health check at http://$APP_IP/api/health (up to 5 mins)..."
$appHealthy = $false
$healthStart = [System.Diagnostics.Stopwatch]::StartNew()
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $resp = Invoke-RestMethod -Uri "http://$APP_IP/api/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($resp -and $resp.status -eq "ok") {
            $appHealthy = $true
            $elapsedSec = [math]::Round($healthStart.Elapsed.TotalSeconds)
            Write-Host "Application is live and responding! (verified in ${elapsedSec}s)"
            break
        }
    } catch {}
    $elapsedSec = [math]::Round($healthStart.Elapsed.TotalSeconds)
    Write-Host "   Waiting for application pods to deploy... (${elapsedSec}s elapsed)"
    Start-Sleep -Seconds 10
}
if (-not $appHealthy) {
    Write-Warning "Application did not respond with status:ok within 5 minutes."
    Write-Warning "Check Jenkins build status at http://$($JENKINS_IP):8080/job/CloudNotes-Pipeline/"
}

Write-Host "========================================="
Write-Host " SUCCESS! Infrastructure & CI/CD Active  "
Write-Host " App URL:    http://$APP_IP"
Write-Host " Jenkins:    http://$($JENKINS_IP):8080"
Write-Host " Grafana:    http://$($APP_IP):3001"
Write-Host " Prometheus: http://$($APP_IP):9091"
Write-Host "========================================="

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

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
        [Parameter(Mandatory = $true)][string]$DockerHubPassword
    )

    $initScript = Join-Path $ProjectRoot "jenkins\init.groovy.d\creds.groovy"
    if (-not (Test-Path -LiteralPath $initScript)) {
        throw "Missing Jenkins init script: $initScript"
    }

    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("cloudnotes-jenkins-secrets-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    $dockerSecret = Join-Path $tempDir "dockerhub_password"
    $sshPassphraseSecret = Join-Path $tempDir "ssh_key_passphrase"
    $installScript = Join-Path $tempDir "install_cloudnotes_creds.sh"
    [System.IO.File]::WriteAllText($dockerSecret, $DockerHubPassword, $Utf8NoBom)
    [System.IO.File]::WriteAllText($sshPassphraseSecret, "", $Utf8NoBom)
    $installScriptContent = @'
set -euo pipefail

sudo mkdir -p /opt/jenkins/init.groovy.d /opt/jenkins/cloudnotes-secrets
sudo mv /tmp/cloudnotes_creds.groovy /opt/jenkins/init.groovy.d/creds.groovy
sudo mv /tmp/cloudnotes_dockerhub_password /opt/jenkins/cloudnotes-secrets/dockerhub_password
sudo mv /tmp/cloudnotes_ssh_key_passphrase /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase
sudo chown -R root:root /opt/jenkins/init.groovy.d
sudo chown -R ubuntu:ubuntu /opt/jenkins/cloudnotes-secrets
sudo chmod 755 /opt/jenkins/init.groovy.d
sudo chmod 700 /opt/jenkins/cloudnotes-secrets
sudo chmod 644 /opt/jenkins/init.groovy.d/creds.groovy
sudo chmod 600 /opt/jenkins/cloudnotes-secrets/app_ssh_private_key /opt/jenkins/cloudnotes-secrets/dockerhub_password /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase

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
  sudo docker cp /opt/jenkins/cloudnotes-secrets/app_ssh_private_key jenkins:/var/jenkins_home/cloudnotes-secrets/app_ssh_private_key
  sudo docker cp /opt/jenkins/cloudnotes-secrets/dockerhub_password jenkins:/var/jenkins_home/cloudnotes-secrets/dockerhub_password
  sudo docker cp /opt/jenkins/cloudnotes-secrets/ssh_key_passphrase jenkins:/var/jenkins_home/cloudnotes-secrets/ssh_key_passphrase
  sudo docker exec jenkins chown -R jenkins:jenkins /var/jenkins_home/init.groovy.d /var/jenkins_home/cloudnotes-secrets
  sudo docker exec jenkins chmod 644 /var/jenkins_home/init.groovy.d/creds.groovy
  sudo docker exec jenkins chmod 600 /var/jenkins_home/cloudnotes-secrets/app_ssh_private_key /var/jenkins_home/cloudnotes-secrets/dockerhub_password /var/jenkins_home/cloudnotes-secrets/ssh_key_passphrase
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
    throw "Missing SSH private key. Specify CLOUDNOTES_SSH_KEY_PATH or place a key at $(Join-Path $env:USERPROFILE '.ssh\cloudnotes-aws') or .secrets\cloudnotes-aws."
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
terraform -chdir=terraform init -no-color | Out-Null

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
Install-JenkinsCredentials -JenkinsIp $JENKINS_IP -DockerHubPassword $DockerHubPassword

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

Write-Host "========================================="
Write-Host " SUCCESS! Everything is deployed."
Write-Host " App URL:    http://$APP_IP"
Write-Host " Jenkins:    http://$($JENKINS_IP):8080"
Write-Host " Grafana:    http://$($APP_IP):3001"
Write-Host " Prometheus: http://$($APP_IP):9091"
Write-Host " "
Write-Host " Note: It will take ~5 mins for Docker to finish"
Write-Host " installing and building the app on the server."
Write-Host "========================================="

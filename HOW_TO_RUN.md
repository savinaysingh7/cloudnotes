# 🚀 How to Run the CloudNotes Project

This project is a full-scale DevOps showcase. You can run it in three different modes. 

---

## 🏗️ 1. Running Locally (Docker Compose)
Use this for quick development and local testing.

1.  **Open Docker Desktop** on your computer and make sure it is running.
2.  Create your local environment file from the template:
    ```powershell
    copy docker/.env.example docker/.env
    ```
3.  Open a terminal (PowerShell) at the root of the project and run:
    ```powershell
    docker-compose -f docker/docker-compose.yml up --build -d
    ```
4.  **Access the app:** [http://localhost:80](http://localhost:80)
5.  **Access Monitoring:**
    *   **Grafana:** [http://localhost:3001](http://localhost:3001) (User: `admin`, Pass: value of `GF_SECURITY_ADMIN_PASSWORD` in `docker/.env`)
    *   **Prometheus:** [http://localhost:9091](http://localhost:9091)

### Recovery
If anything goes wrong, run:
```powershell
powershell -File docker/recover.ps1
```

---

## ☸️ 2. Running in Kubernetes (Minikube)
Use this to demonstrate orchestration and self-healing.

1.  **Start Minikube:**
    ```powershell
    minikube start --driver=docker
    ```
2.  **Apply Manifests:**
    ```powershell
    kubectl apply -f kubernetes/
    ```
3.  **Open the App:**
    ```powershell
    minikube service frontend -n cloudnotes
    ```

---

## ☁️ 3. Running in AWS Cloud (Production)
This is your real, live internet deployment.

*   **Production App:** [http://13.206.199.155](http://13.206.199.155)
*   **Jenkins CI/CD:** [http://13.201.50.42:8080](http://13.201.50.42:8080)
    *   **User:** `admin`
    *   **Password:** `CHANGE_ME` (set in `jenkins/jenkins.yaml` before deployment)

---

## 🔄 4. How to Trigger the Automated Pipeline
1.  Change any file in your project (e.g., add a comment to `README.md`).
2.  **Push to GitHub:**
    ```powershell
    git add .
    git commit -m "Testing automation"
    git push origin main
    ```
3.  **Jenkins will automatically detect the change** within 60 seconds and start a new build. It will:
    *   Run a **security scan** (truffleHog) for leaked secrets.
    *   Build new Docker images.
    *   Run backend unit tests (pytest).
    *   Run an **image vulnerability scan** (Trivy) for CVEs.
    *   Push images to Docker Hub.
    *   **Securely update the AWS Production App via SSH.**

---

## ✨ 5. App Features (v2.0)
- **Create** notes with title and body
- **Read** all notes with timestamps
- **Update** notes via the Edit button
- **Delete** notes
- **Search** notes by title or body content
- **Dark mode** modern UI with animations
- **Prometheus metrics** at `/metrics` endpoint
- **Grafana dashboard** with 6 monitoring panels

---

## 🔧 6. Manual Setup Steps (Optional Enhancements)

### HTTPS / TLS Certificate
To add SSL to the AWS production server:
```bash
ssh -i cloudnotes_key ubuntu@YOUR_NEW_APP_IP
sudo apt install -y certbot
sudo certbot certonly --standalone -d your-domain.com
# Then configure Nginx to use the cert
```

### GitHub Webhooks (Instead of Polling)
1. Go to your GitHub repo → Settings → Webhooks
2. Add webhook URL: `http://YOUR_NEW_JENKINS_IP:8080/github-webhook/`
3. Content type: `application/json`
4. Events: Just the `push` event
5. Remove `pollSCM` from Jenkinsfile and add `githubPush()` trigger

### Terraform Remote State
See `terraform/backend.tf.example` for S3 remote state configuration.

---

## 🛑 How to Delete Everything (To save costs)
Once your demo is finished, run this from the project root to avoid AWS charges:
```powershell
terraform -chdir=terraform destroy -auto-approve
```

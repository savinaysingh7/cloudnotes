# 🚀 How to Run the CloudNotes Project

This project is a full-scale DevOps showcase. You can run it in three different modes. 

---

## 🏗️ 1. Running Locally (Docker Compose)
Use this for quick development and local testing.

1.  **Open Docker Desktop** on your computer and make sure it is running.
2.  Open a terminal (PowerShell) and run:
    ```powershell
    cd docker
    docker-compose up --build -d
    ```
3.  **Access the app:** [http://localhost:80](http://localhost:80)
4.  **Access Monitoring:**
    *   **Grafana:** [http://localhost:3001](http://localhost:3001) (User: `admin`, Pass: `admin`)
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

*   **Production App:** [http://3.235.124.255](http://3.235.124.255)
*   **Jenkins CI/CD:** [http://3.234.255.197:8080](http://3.234.255.197:8080)
    *   **User:** `admin`
    *   **Password:** `8767317fd394488ba28b0f28445c1d44`

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
ssh -i cloudnotes_key ubuntu@3.235.124.255
sudo apt install -y certbot
sudo certbot certonly --standalone -d your-domain.com
# Then configure Nginx to use the cert
```

### GitHub Webhooks (Instead of Polling)
1. Go to your GitHub repo → Settings → Webhooks
2. Add webhook URL: `http://3.234.255.197:8080/github-webhook/`
3. Content type: `application/json`
4. Events: Just the `push` event
5. Remove `pollSCM` from Jenkinsfile and add `githubPush()` trigger

### Terraform Remote State
See `terraform/backend.tf.example` for S3 remote state configuration.

---

## 🛑 How to Delete Everything (To save costs)
Once your demo is finished, run this to avoid AWS charges:
```powershell
cd terraform
terraform destroy -auto-approve
```

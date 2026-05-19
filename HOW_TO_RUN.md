# 🚀 How to Run the CloudNotes Project

This project is a full-scale DevOps showcase. You can run it in three different modes. 

---

## 🏗️ 1. Running Locally (Docker Compose)
Use this for quick development and local testing.

1.  **Open Docker Desktop** on your computer and make sure it is running.
2.  Open a terminal (PowerShell) and run:
    ```powershell
    cd docker
    docker-compose up -d
    ```
3.  **Access the app:** [http://localhost:80](http://localhost:80)
4.  **Access Monitoring:** [http://localhost:3001](http://localhost:3001) (User: `admin`, Pass: `admin`)

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
    *   Build new images.
    *   Run tests.
    *   Push to Docker Hub.
    *   **Securely update the AWS Production App via SSH.**

---

## 🛑 How to Delete Everything (To save costs)
Once your demo is finished, run this to avoid AWS charges:
```powershell
cd terraform
terraform destroy -auto-approve
```

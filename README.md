# CloudNotes — Full DevOps Showcase

CloudNotes is a containerized note-taking application designed to demonstrate the complete DevOps lifecycle, covering all 5 units of the syllabus.

## 🚀 Quick Links (Live Project)
*   **Production App (AWS):** [http://13.206.199.155](http://13.206.199.155)
*   **Jenkins CI/CD (AWS):** [http://13.201.29.106:8080](http://13.201.29.106:8080)
*   **Monitoring (Local):** [http://localhost:3001](http://localhost:3001)

---

## 🛠️ Project Architecture

### 📦 Unit II: Containerization & Orchestration
*   **Docker:** Multi-stage builds for Flask (Backend) and Nginx (Frontend).
*   **Kubernetes:** Fully managed manifests in the `kubernetes/` folder, verified on Minikube.
*   **Docker Compose:** Seamless local development environment with Postgres integration.

### 🏗️ Unit III: Infrastructure as Code (IaC)
*   **Terraform:** Modular infrastructure provisioning on AWS.
*   **Resources:** VPC, Public Subnets, Security Groups, EC2 (App & Jenkins), and S3.
*   **Automation:** Zero-touch deployment using EC2 `user_data` scripts.

### 🔄 Unit IV: CI/CD Pipeline
*   **Jenkins:** Automated pipeline defined in `jenkins/Jenkinsfile`.
*   **Stages:** 
    1. Checkout 
    2. Backend Tests (Pytest) 
    3. Docker Build & Push 
    4. Kubernetes Rollout.

### 📊 Unit V: Monitoring & Security
*   **Prometheus:** Scraping real-time application metrics from the Flask `/metrics` endpoint.
*   **Grafana:** Visualizing data (Note count, Request rate) on a custom dashboard.
*   **Security:** IAM least-privilege roles and Security Group isolation.

---

## 💻 Local Setup

1.  **Clone the Repo:**
    ```bash
    git clone <your-repo-url>
    ```
2.  **Run with Docker Compose:**
    ```bash
    docker-compose -f docker/docker-compose.yml up --build
    ```
3.  **Deploy to K8s:**
    ```bash
    kubectl apply -f kubernetes/
    ```

## 👨‍🎓 Educational Mapping
*   **Unit I:** Git Branching, GitHub, and Public Cloud Deployment.
*   **Unit II:** Virtualization vs Containerization, K8s Pods/Services.
*   **Unit III:** IaC Principles, AWS Cloud Services.
*   **Unit IV:** CI/CD Methodologies, Jenkins Pipelines.
*   **Unit V:** Observability, Metrics, and DevSecOps.

---
*Developed for the Cloud & DevOps Fundamentals Course.*


---
*This commit was made to test the automated Jenkins pipeline trigger.*

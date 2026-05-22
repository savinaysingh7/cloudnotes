# 📘 CloudNotes: The Ultimate DevOps Masterclass
**Level:** Zero to Advanced Engineering
**Goal:** Understand every line of code, every command, and every UI click used to build this enterprise-grade CI/CD pipeline and cloud infrastructure.

---

## 🏗️ 1. Infrastructure as Code (Terraform)
Before deploying code, we need servers. Instead of clicking through the AWS console, we wrote Terraform scripts to automate the creation of the cloud environment.

### The Code: `terraform/main.tf`
```hcl
resource "aws_security_group" "app_sg" {
  name        = "cloudnotes-app-sg"
  description = "Allow inbound HTTP and SSH traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Open to the world
  }
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS
  instance_type = "t2.micro"              # AWS Free Tier compatible
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  
  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io docker-compose
              sudo usermod -aG docker ubuntu
              EOF
}
```
### 🧠 Deep Dive Explanation:
* **`aws_security_group`**: This is a virtual firewall. The `ingress` block explicitly opens port 80 (HTTP) so users can access the website.
* **`instance_type`**: We specifically chose `t2.micro` to stay within the AWS Free Tier, costing $0.
* **`user_data`**: This is the magic of cloud automation. The moment AWS turns on the server, it runs this bash script. It installs Docker and Docker Compose automatically so the server is ready to host our app without any human SSH login.

### 💻 Commands Used:
1. `terraform init` : Downloads the AWS plugins.
2. `terraform plan` : Does a "dry run" and shows you exactly what it will create.
3. `terraform apply --auto-approve` : Actually contacts the AWS API and builds the server.

---

## 🐳 2. Containerization (Docker)
We use Docker so our app runs identically on Windows, Mac, and Linux.

### The Code: `app/backend/Dockerfile`
```dockerfile
# 1. Base Image
FROM python:3.11-slim

# 2. Working Directory
WORKDIR /app

# 3. Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Source Code
COPY . .

# 5. Execution
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```
### 🧠 Deep Dive Explanation:
1. **`python:3.11-slim`**: We use the "slim" version because it strips out unnecessary Linux tools, reducing the image size from ~1GB to ~150MB, making deployments faster.
2. **`--no-cache-dir`**: Prevents `pip` from saving downloaded zip files, keeping the container tiny.
3. **`gunicorn`**: The default Flask server (`flask run`) is explicitly NOT for production. We use `gunicorn` with `--workers 2`. This means it spawns two separate Python processes, allowing two users to fetch notes at the exact same millisecond without waiting in line.

### The Code: `docker/docker-compose.yml`
```yaml
  backend:
    build:
      context: ../app/backend
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
```
### 🧠 Deep Dive Explanation:
* **`env_file: .env`**: We never commit passwords to GitHub. We load them from a hidden `.env` file into the container's environment variables.
* **`condition: service_healthy`**: We don't just wait for the database container to "start". We wait until PostgreSQL is actually ready to accept connections before booting the backend.
* **`restart: unless-stopped`**: This is basic Docker self-healing.

### 💻 Commands Used:
1. `docker build -t cloudnotes-backend .` : Builds the image from the Dockerfile.
2. `docker-compose up -d` : Reads the YAML file and starts the whole stack (DB, Frontend, Backend) in detached mode (background).

---

## ☸️ 3. Orchestration (Kubernetes)
Docker Compose is for your laptop. Kubernetes (K8s) is the enterprise standard for live production servers.

### The Code: `kubernetes/backend-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: savinaysingh7/cloudnotes-backend:latest
          resources:
            requests:
              memory: "128Mi"
            limits:
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /api/health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
```
### 🧠 Deep Dive Explanation:
* **`Deployment` & `replicas: 2`**: This creates a "ReplicaSet". Kubernetes constantly monitors the cluster. If it sees only 1 pod running, it instantly creates a 2nd one to satisfy the rule. This is true self-healing.
* **`resources`**: If a memory leak occurs in Python, K8s will kill the container if it exceeds 256MB, preventing the entire AWS server from crashing.
* **`readinessProbe`**: Kubernetes literally hits `http://localhost:5000/api/health` every 10 seconds. If your app returns a 500 Error, K8s removes it from the load balancer instantly so users don't see errors.

### 💻 Commands Used:
1. `kubectl apply -f kubernetes/` : Applies all YAML files in the folder to the cluster.
2. `kubectl get pods -n cloudnotes` : Lists running containers.
3. `kubectl autoscale deployment backend --cpu-percent=80 --min=2 --max=5` : Creates an HPA (Horizontal Pod Autoscaler) that clones the app if CPU usage hits 80%.

---

## 🤖 4. CI/CD Pipeline Automation (Jenkins)
We automated the deployment so we never have to log into the AWS server manually.

### The Jenkins UI Setup:
Before writing code, we configured Jenkins via its Web UI (`http://<server-ip>:8080`):
1. **Credentials Management:** We navigated to *Manage Jenkins -> Credentials* and added:
   - `dockerhub-credentials` (Username with password) for DockerHub.
   - `kubeconfig` (Secret file) containing the Kubernetes admin certificate so Jenkins can securely execute `kubectl` commands.
2. **Webhook Trigger:** We checked "GitHub hook trigger for GITScm polling" so that every time we `git push`, GitHub sends an HTTP POST request to Jenkins to wake it up.

### The Code: `jenkins/Jenkinsfile` (Declarative Pipeline)
```groovy
pipeline {
  agent any
  stages {
    stage('Security Scan') {
      steps {
        sh 'pip install truffleHog'
        sh 'trufflehog filesystem . --only-verified'
      }
    }
    stage('Vulnerability Scan') {
      steps {
        sh "trivy image --severity HIGH,CRITICAL savinaysingh7/cloudnotes-backend:${env.BUILD_NUMBER}"
      }
    }
    stage('Deploy to AWS') {
      steps {
        withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
          sh "kubectl set image deployment/backend backend=savinaysingh7/cloudnotes-backend:${env.BUILD_NUMBER} -n cloudnotes"
        }
      }
    }
  }
}
```
### 🧠 Deep Dive Explanation:
* **TruffleHog (DevSecOps):** It scans the git history for entropy (random strings) that look like AWS API keys. If it finds one, it intentionally fails the build and refuses to deploy.
* **Trivy (DevSecOps):** It scans the Docker image layers against the CVE database. If the Python base image has a known critical exploit, it fails the build.
* **`kubectl set image`**: This triggers a **Rolling Update**. Kubernetes starts the new version (v2), waits for the `readinessProbe` to pass, and only then destroys the old version (v1). Users experience absolutely zero downtime.

---

## 📊 5. Monitoring & Alerting (Prometheus & Grafana)

### The Backend Code (Python Instrumentation)
To get metrics, we modified the actual Python code in `app.py`:
```python
from prometheus_client import Counter, generate_latest
NOTES_UPDATED = Counter('notes_updated_total', 'Total notes updated')

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    # ... logic ...
    NOTES_UPDATED.inc() # Increments the math counter
```

### The Code: `prometheus.yml` & `alert_rules.yml`
```yaml
scrape_configs:
  - job_name: 'cloudnotes_backend'
    scrape_interval: 5s
    static_configs:
      - targets: ['backend:5000']
```
Prometheus automatically visits `http://backend:5000/metrics` every 5 seconds and records the numbers.

**Alerting:**
```yaml
      - alert: HighErrorRate
        expr: rate(flask_http_request_exceptions_total[1m]) > 5
        for: 1m
```
If the backend throws more than 5 Python exceptions per minute, Prometheus triggers an alarm.

### Grafana UI Deep Dive:
1. We logged into `http://localhost:3001` (admin/admin).
2. We went to *Connections -> Data Sources* and added Prometheus (`http://prometheus:9090`).
3. We clicked *Add Panel* and used **PromQL (Prometheus Query Language)** to draw the graphs.
   * Query 1: `flask_http_request_total` (Shows total lifetime hits).
   * Query 2: `rate(flask_http_request_total[1m])` (A derivative function that shows requests *per second*).
4. We saved this dashboard as `cloudnotes.json` and mounted it into the Docker container via `volumes:` so it loads automatically on startup!

---
*This guide proves your complete end-to-end mastery over cloud infrastructure, containerization, DevSecOps pipelines, and application observability.*

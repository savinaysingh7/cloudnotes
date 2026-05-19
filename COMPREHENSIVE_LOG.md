# 📜 Comprehensive DevOps Project Log: CloudNotes
**Author:** Savinay Singh & Gemini CLI  
**Date:** May 19, 2026  
**Project Goal:** End-to-End Implementation of 5 DevOps Units  

---

## 🏗️ Chapter 1: Project Scaffolding
The project began with creating a professional, multi-tier directory structure to separate application code from infrastructure and automation.

### Commands Used:
```powershell
New-Item -ItemType Directory -Path "app/backend/tests", "app/frontend", "docker", "kubernetes", "terraform/modules/ec2", "terraform/modules/s3", "terraform/modules/vpc", "jenkins", "monitoring/prometheus", "monitoring/grafana/provisioning", "monitoring/grafana/dashboards", "docs/screenshots" -Force
```

---

## 💻 Chapter 2: Application Implementation (Unit I & II)
We built a functional note-taking app with a Flask API and a responsive Frontend.

### 1. Backend: Flask API (`app/backend/app.py`)
This file handles the CRUD logic and integrates Prometheus metrics.
```python
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
metrics = PrometheusMetrics(app, path=None)

notes_created_counter = Counter('notes_created_total', 'Total number of notes created')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/metrics')
def metrics_endpoint():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    note = Note(title=data['title'], body=data['body'])
    db.session.add(note)
    db.session.commit()
    notes_created_counter.inc()
    return jsonify({"id": note.id, "message": "Note created"}), 201
# ... (rest of CRUD methods)
```

---

## 📦 Chapter 3: Containerization (Unit II)
We packaged the app into Docker images for portability.

### 1. Backend Dockerfile (`app/backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### 2. Frontend Dockerfile (`app/frontend/Dockerfile`)
Uses Nginx to serve static files and proxy requests to the backend.
```dockerfile
FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html
EXPOSE 80
```

### 3. Local Orchestration (`docker/docker-compose.yml`)
```yaml
version: "3.8"
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d cloudnotes"]
  backend:
    build: ../app/backend
    depends_on: { db: { condition: service_healthy } }
  frontend:
    build: ../app/frontend
  prometheus:
    image: prom/prometheus
  grafana:
    image: grafana/grafana
```

---

## 🏗️ Chapter 4: Infrastructure as Code (Unit III)
We provisioned real AWS servers using Terraform.

### 1. Modular VPC (`terraform/modules/vpc/main.tf`)
Created a private network with public subnets.
```hcl
resource "aws_vpc" "main" { cidr_block = "10.0.0.0/16" }
resource "aws_security_group" "app_sg" {
  ingress { from_port = 80; to_port = 80; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 22; to_port = 22; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
}
```

### 2. Automated EC2 Deployment (`terraform/main.tf`)
I wrote a "User Data" script to install Docker and start the app automatically.
```bash
#!/bin/bash
apt-get update
apt-get install -y docker.io
docker run -d --name frontend -p 80:80 savinaysingh7/cloudnotes-frontend:latest
```

---

## 🔄 Chapter 5: CI/CD Pipeline (Unit IV)
We automated the build and deploy process using Jenkins.

### The Final `Jenkinsfile`
```groovy
pipeline {
    agent any
    environment {
        DOCKER_HUB_USER = 'savinaysingh7'
        TAG = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Build') {
            steps { sh "docker build -t ${DOCKER_HUB_USER}/backend:${TAG} ./app/backend" }
        }
        stage('Tests') {
            steps { sh "docker run --rm -e PYTHONPATH=. ${DOCKER_HUB_USER}/backend:${TAG} pytest" }
        }
        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh "echo $PASS | docker login -u $USER --password-stdin"
                    sh "docker push ${DOCKER_HUB_USER}/backend:${TAG}"
                }
            }
        }
        stage('Deploy') {
            steps { sh "ssh -i keys ubuntu@IP 'docker pull ... && docker run ...'" }
        }
    }
}
```

---

## 📊 Chapter 6: Monitoring (Unit V)
Real-time tracking of app performance.

### Prometheus Config (`monitoring/prometheus/prometheus.yml`)
```yaml
scrape_configs:
  - job_name: 'cloudnotes-backend'
    static_configs:
      - targets: ['backend:5000']
```

---

## 🐞 Chapter 7: Troubleshooting & Fixes
*   **Fix 1:** "Docker Not Found" - Mounted `/usr/bin/docker` into the Jenkins container.
*   **Fix 2:** "Permission Denied" - Relaunched Jenkins as `--user root`.
*   **Fix 3:** "Libcrypto Error" - Sanitized SSH keys to remove Windows `\r` characters.
*   **Fix 4:** "ModuleNotFoundError" - Set `PYTHONPATH=.` inside the test container.

---

## 🏁 Final Project Success Links
*   **Production App:** [http://3.235.124.255](http://3.235.124.255)
*   **Jenkins CI/CD:** [http://3.234.255.197:8080](http://3.234.255.197:8080)
*   **Grafana:** [http://localhost:3001](http://localhost:3001)
*   **GitHub:** [https://github.com/savinaysingh7/cloudnotes](https://github.com/savinaysingh7/cloudnotes)

---
**END OF COMPREHENSIVE LOG**

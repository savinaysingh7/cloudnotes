## Project Idea: **"CloudNotes" — A Containerized Note-Taking App with Full DevOps Pipeline**

A simple, multi-tier note-taking web app that acts as a *living showcase* of every unit in your syllabus. The beauty is that the app itself is modest (so you focus on the DevOps, not the code), but the infrastructure around it is rich.

---

### What the App Does
A basic REST API + frontend where users can **Create / Read / Delete short notes**. That's it. The simplicity is intentional — all the complexity lives in the pipeline and infrastructure.

---

### How Each Unit Maps to the Project

**Unit I — Cloud & DevOps Fundamentals / Git**
- Host the entire project on a **GitHub repository** with proper branching (`main`, `dev`, `feature/*`)
- Write a `README.md` that documents the architecture
- Deploy the app on a **public cloud** (AWS/GCP free tier) to demonstrate IaaS/PaaS/SaaS differences

**Unit II — Virtualization & Containers**
- Package the frontend (React/plain HTML) and backend (Flask/Node) as **separate Docker containers**
- Write a `docker-compose.yml` for local dev (demonstrates Docker architecture & lifecycle)
- Use **Kubernetes (Minikube locally or GKE/EKS free tier)** to orchestrate the containers with `Deployment` + `Service` YAML files

**Unit III — IaC & Cloud Services**
- Write **Terraform scripts** to provision:
  - An EC2 instance (or GCP VM) for the app
  - An S3 bucket for static frontend hosting
  - A security group / VPC
- Optionally add an **AWS Lambda** function for a "random note of the day" feature to showcase serverless

**Unit IV — CI/CD**
- Set up a **Jenkins pipeline** (can run in Docker itself) with stages:
  1. `Build` — build Docker images
  2. `Test` — run unit tests
  3. `Push` — push image to Docker Hub
  4. `Deploy` — trigger Kubernetes rollout
- Every `git push` to `main` triggers the full pipeline automatically

**Unit V — Monitoring & Security**
- Add **Prometheus** to scrape metrics from the backend (request count, latency)
- Visualize in a **Grafana dashboard** (notes created per hour, error rate)
- Set up **AWS IAM roles** so Jenkins only has the minimum permissions needed (DevSecOps principle)
- Add a simple **secrets scan** step in the pipeline (e.g., `truffleHog` or `git-secrets`)

---

### Architecture at a Glance

```
GitHub Repo
    │
    └──► Jenkins (CI/CD)
              │
    ┌─────────┼──────────┐
  Build     Test       Deploy
  Docker    pytest/    kubectl apply
  Image     jest       (Kubernetes)
              │
         Docker Hub
              │
         ┌────┴────┐
      Frontend   Backend API
      (Nginx)    (Flask/Node)
                     │
                  PostgreSQL
                  (K8s Pod)
                     │
              Prometheus + Grafana
              (Monitoring Layer)
                     │
             Terraform (provisions
             all cloud resources)
```

---

### Why This Project Works Well

- **Scope is controlled** — the actual app is tiny, so it won't overwhelm you
- **Every unit has a deliverable** — Dockerfile, Terraform file, Jenkinsfile, Grafana dashboard, IAM policy
- **It's demonstrable live** — you can show the pipeline running, a deploy happening in real time, and metrics updating
- **Free tier friendly** — AWS/GCP free tier + Minikube keeps cost at ₹0
- **Unique angle** — the app *monitors its own deployment*, which is a satisfying meta-story to tell during a demo

---

### Suggested Tech Stack

| Layer | Tool |
|---|---|
| App | Flask (Python) + plain HTML or React |
| Container | Docker + Docker Compose |
| Orchestration | Kubernetes (Minikube or GKE) |
| IaC | Terraform |
| Cloud | AWS (EC2, S3, Lambda) or GCP |
| CI/CD | Jenkins |
| Monitoring | Prometheus + Grafana |
| Security | IAM + truffleHog in pipeline |
| Source Control | Git + GitHub |

Now let me build the full detailed project plan as a well-structured markdown document.Here's your complete project plan! Here's a summary of what's inside:

---

### What's Covered

**Folder Structure** — A production-style layout with `app/`, `docker/`, `kubernetes/`, `terraform/`, `jenkins/`, and `monitoring/` directories, each with every file you'll need.

**Unit-by-Unit Tasks** — Each unit has concrete, numbered tasks with exact commands, config snippets, and explanations of what concept each task demonstrates:
- Unit I → GitHub repo setup, branching strategy, manual EC2 deploy
- Unit II → Dockerfiles, docker-compose, full Kubernetes manifests
- Unit III → Terraform modules for VPC/EC2/S3, Lambda bonus feature, cost analysis
- Unit IV → Full 6-stage Jenkinsfile with webhook auto-trigger
- Unit V → Prometheus + Grafana setup, IAM policy, K8s RBAC, secrets scanning

**Ready-to-Use Starter Code** — Flask app, requirements.txt, Kubernetes deployment YAML, and .gitignore all included verbatim.

**4-Week Sprint Plan** — Day-by-day breakdown so you always know what to build next.

**Evaluation Checklist** — 20 checkboxes across all 5 units to verify completeness before your demo.

---

The total cost to run this on **AWS Free Tier** is effectively ₹0 for the first 12 months. Let me know if you want starter code for any specific file expanded further!


# CloudNotes — Full DevOps Project Plan
### A Containerized Note-Taking App Covering All 5 Units of Cloud & DevOps

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Folder Structure](#3-folder-structure)
4. [Unit-wise Implementation Plan](#4-unit-wise-implementation-plan)
   - Unit I : Git & Cloud Fundamentals
   - Unit II : Docker & Kubernetes
   - Unit III : Terraform & Cloud Services
   - Unit IV : Jenkins CI/CD Pipeline
   - Unit V : Prometheus, Grafana & Security
5. [Step-by-Step Build Guide](#5-step-by-step-build-guide)
6. [Starter Code & Config Files](#6-starter-code--config-files)
7. [Timeline / Sprint Plan](#7-timeline--sprint-plan)
8. [Tools & Free Resources](#8-tools--free-resources)
9. [Evaluation Checklist](#9-evaluation-checklist)

---

## 1. Project Overview

**Project Name:** CloudNotes
**Type:** Full-stack micro web application with complete DevOps infrastructure
**Tech Stack:** Python (Flask) · Docker · Kubernetes · Terraform · Jenkins · Prometheus · Grafana · AWS Free Tier

### What the App Does
CloudNotes is a simple REST API + web frontend that lets users:
- Create a short note (title + body)
- View all notes
- Delete a note

The app itself is intentionally minimal. All learning value is in the **infrastructure, pipeline, and operations** surrounding it.

### Why This Works for All 5 Units

| Unit | Deliverable in This Project |
|------|----------------------------|
| I | GitHub repo with branching, hosted on AWS (public cloud) |
| II | Docker containers + Kubernetes deployment |
| III | Terraform scripts to provision AWS infra |
| IV | Jenkins pipeline: build → test → push → deploy |
| V | Prometheus metrics + Grafana dashboard + IAM + secrets scan |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPER MACHINE                        │
│                                                                 │
│   Code Editor  ──► git push ──► GitHub Repository              │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Webhook trigger
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     JENKINS SERVER (EC2)                        │
│                                                                 │
│  Stage 1: Checkout  ──► Stage 2: Test  ──► Stage 3: Build      │
│  Stage 4: Push to Docker Hub  ──► Stage 5: Deploy to K8s       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Docker Hub        AWS S3           Kubernetes Cluster
       (Image Store)   (Static Files)    (Minikube / GKE)
                                               │
                               ┌───────────────┼───────────────┐
                               ▼               ▼               ▼
                          Frontend Pod    Backend Pod     PostgreSQL Pod
                          (Nginx:80)    (Flask:5000)       (DB:5432)
                               │               │
                               └───────┬───────┘
                                       ▼
                              Prometheus (Metrics Scrape)
                                       │
                                       ▼
                              Grafana Dashboard (Port 3000)
```

---

## 3. Folder Structure

```
cloudnotes/
│
├── README.md                          # Project documentation
├── .gitignore                         # Git ignore rules
├── .git/                              # Git repository data
│
├── app/                               # Application source code
│   ├── backend/                       # Flask REST API
│   │   ├── app.py                     # Main Flask application
│   │   ├── models.py                  # Database models
│   │   ├── requirements.txt           # Python dependencies
│   │   ├── Dockerfile                 # Backend container definition
│   │   └── tests/
│   │       ├── test_app.py            # Unit tests
│   │       └── test_models.py        # Model tests
│   │
│   └── frontend/                      # Static HTML + JS UI
│       ├── index.html                 # Main page
│       ├── style.css                  # Styles
│       ├── app.js                     # API calls via fetch()
│       └── Dockerfile                 # Nginx-based container
│
├── docker/                            # Docker configuration
│   ├── docker-compose.yml             # Local development setup
│   └── docker-compose.prod.yml        # Production override
│
├── kubernetes/                        # K8s manifests
│   ├── namespace.yaml                 # cloudnotes namespace
│   ├── backend-deployment.yaml        # Backend pods
│   ├── backend-service.yaml           # ClusterIP service
│   ├── frontend-deployment.yaml       # Frontend pods
│   ├── frontend-service.yaml          # NodePort / LoadBalancer
│   ├── postgres-deployment.yaml       # PostgreSQL statefulset
│   ├── postgres-pvc.yaml              # Persistent volume claim
│   ├── postgres-secret.yaml           # DB credentials (base64)
│   └── ingress.yaml                   # Ingress controller config
│
├── terraform/                         # Infrastructure as Code
│   ├── main.tf                        # Root Terraform config
│   ├── variables.tf                   # Input variables
│   ├── outputs.tf                     # Output values
│   ├── provider.tf                    # AWS provider config
│   └── modules/
│       ├── ec2/                       # EC2 instance module
│       │   ├── main.tf
│       │   └── variables.tf
│       ├── s3/                        # S3 bucket module
│       │   ├── main.tf
│       │   └── variables.tf
│       └── vpc/                       # VPC & security groups
│           ├── main.tf
│           └── variables.tf
│
├── jenkins/                           # CI/CD Pipeline
│   ├── Jenkinsfile                    # Declarative pipeline script
│   └── jenkins-docker-compose.yml     # Run Jenkins in Docker
│
├── monitoring/                        # Observability stack
│   ├── prometheus/
│   │   ├── prometheus.yml             # Scrape configuration
│   │   └── alert_rules.yml            # Alert definitions
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources.yaml       # Auto-configure Prometheus
│       │   └── dashboards.yaml        # Auto-load dashboards
│       └── dashboards/
│           └── cloudnotes.json        # Custom dashboard JSON
│
└── docs/                              # Documentation
    ├── architecture.png               # Architecture diagram
    ├── setup.md                       # Local setup guide
    └── screenshots/                   # Demo screenshots
```

---

## 4. Unit-wise Implementation Plan

---

### UNIT I — Introduction to Cloud and DevOps Fundamentals

**Goal:** Set up the project repository, understand cloud models, and deploy on public cloud.

#### Tasks

**1.1 — Initialize Git Repository**
```bash
git init cloudnotes
cd cloudnotes
git checkout -b main
# Create .gitignore, README.md
git add .
git commit -m "feat: initial project scaffold"
git remote add origin https://github.com/<your-username>/cloudnotes.git
git push -u origin main
```

**1.2 — Git Branching Strategy**
```
main          ← stable, production-ready code
  └── dev     ← integration branch
        └── feature/backend-api
        └── feature/frontend-ui
        └── feature/docker-setup
```

**1.3 — Demonstrate Cloud Delivery Models**
Document in README.md how CloudNotes uses each model:
- **IaaS** → AWS EC2 (we manage the OS, runtime, app)
- **PaaS** → AWS Elastic Beanstalk (we only manage the app)
- **SaaS** → Using GitHub as a SaaS tool for source control

**1.4 — Deploy manually on AWS EC2 (public cloud)**
```bash
# SSH into your EC2 instance
ssh -i keypair.pem ubuntu@<EC2-IP>

# Install dependencies
sudo apt update && sudo apt install -y python3-pip
pip3 install flask flask-sqlalchemy

# Run the app directly (no Docker yet — show IaaS style)
python3 app.py
```

**Key Concepts Demonstrated:**
- Git lifecycle: init → add → commit → push → pull → branch → merge
- Remote repositories and collaboration workflows
- Public vs Private cloud (EC2 = public, your laptop = private)
- IaaS, PaaS, SaaS with real examples

---

### UNIT II — Virtualization, Containerization, and Kubernetes

**Goal:** Package the app with Docker and orchestrate with Kubernetes.

#### Tasks

**2.1 — Write Backend Dockerfile**
```dockerfile
# app/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**2.2 — Write Frontend Dockerfile**
```dockerfile
# app/frontend/Dockerfile
FROM nginx:alpine

COPY . /usr/share/nginx/html

EXPOSE 80
```

**2.3 — Docker Compose for Local Development**
```yaml
# docker/docker-compose.yml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cloudnotes
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret123
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ../app/backend
    environment:
      DATABASE_URL: postgresql://admin:secret123@db:5432/cloudnotes
    ports:
      - "5000:5000"
    depends_on:
      - db

  frontend:
    build: ../app/frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

**2.4 — Build and Run Locally**
```bash
docker-compose -f docker/docker-compose.yml up --build
# Frontend: http://localhost:80
# Backend:  http://localhost:5000/api/notes
```

**2.5 — Push Images to Docker Hub**
```bash
docker build -t <username>/cloudnotes-backend:v1 ./app/backend
docker build -t <username>/cloudnotes-frontend:v1 ./app/frontend
docker push <username>/cloudnotes-backend:v1
docker push <username>/cloudnotes-frontend:v1
```

**2.6 — Deploy to Kubernetes (Minikube)**
```bash
# Start Minikube
minikube start

# Apply all manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/postgres-secret.yaml
kubectl apply -f kubernetes/postgres-pvc.yaml
kubectl apply -f kubernetes/postgres-deployment.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/backend-service.yaml
kubectl apply -f kubernetes/frontend-service.yaml

# Check status
kubectl get pods -n cloudnotes
kubectl get services -n cloudnotes

# Access the app
minikube service frontend-service -n cloudnotes
```

**Key Concepts Demonstrated:**
- Virtualization vs Containerization comparison
- Docker architecture: Client → Daemon → Registry
- Docker image layers and caching
- Docker lifecycle: build → run → stop → rm
- Kubernetes: Pods, Deployments, Services, Namespaces
- PersistentVolumeClaims for stateful data

---

### UNIT III — Infrastructure as Code and Cloud Services

**Goal:** Provision all AWS infrastructure automatically using Terraform.

#### Tasks

**3.1 — Terraform Provider Config**
```hcl
# terraform/provider.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

**3.2 — Variables**
```hcl
# terraform/variables.tf
variable "aws_region"       { default = "us-east-1" }
variable "instance_type"    { default = "t2.micro" }   # Free tier
variable "project_name"     { default = "cloudnotes" }
variable "environment"      { default = "dev" }
```

**3.3 — Main Infrastructure**
```hcl
# terraform/main.tf

# VPC
module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
}

# EC2 Instance for Jenkins
module "jenkins_ec2" {
  source        = "./modules/ec2"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.vpc.jenkins_sg_id
  name          = "${var.project_name}-jenkins"
}

# EC2 Instance for the App
module "app_ec2" {
  source        = "./modules/ec2"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.vpc.app_sg_id
  name          = "${var.project_name}-app"
}

# S3 Bucket for frontend static files (backup/CDN)
module "frontend_bucket" {
  source       = "./modules/s3"
  bucket_name  = "${var.project_name}-frontend-${var.environment}"
}
```

**3.4 — Terraform Commands**
```bash
cd terraform/
terraform init           # Download providers
terraform plan           # Preview changes
terraform apply          # Create resources
terraform output         # Show IPs and URLs
terraform destroy        # Tear down everything (save costs)
```

**3.5 — AWS Lambda (Bonus Feature)**
Add a "Note of the Day" button in the UI that calls a Lambda function which returns a random note from the database. This showcases:
- Serverless computing (FaaS)
- AWS Lambda + API Gateway
- Event-driven architecture

**3.6 — Cloud Economics Notes**
Document in `docs/setup.md`:
- EC2 t2.micro: Free for 12 months (750 hrs/month)
- S3: 5 GB free tier storage
- Lambda: 1 million free requests/month
- Total estimated monthly cost after free tier: ~$10-15/month
- TCO calculation showing on-premise vs cloud comparison

**Key Concepts Demonstrated:**
- IaC principles: idempotency, version control, automation
- Terraform: providers, resources, modules, state files
- AWS EC2, S3, Lambda, VPC, Security Groups
- Cloud pricing and TCO fundamentals

---

### UNIT IV — CI/CD Pipeline with Jenkins

**Goal:** Automate the entire build, test, and deployment workflow.

#### Tasks

**4.1 — Run Jenkins in Docker**
```yaml
# jenkins/jenkins-docker-compose.yml
version: "3.8"
services:
  jenkins:
    image: jenkins/jenkins:lts
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
volumes:
  jenkins_home:
```

```bash
docker-compose -f jenkins/jenkins-docker-compose.yml up -d
# Access Jenkins: http://localhost:8080
```

**4.2 — Jenkinsfile (Declarative Pipeline)**
```groovy
// jenkins/Jenkinsfile
pipeline {
  agent any

  environment {
    DOCKERHUB_CREDS  = credentials('dockerhub-credentials')
    DOCKER_IMAGE_BE  = "your-username/cloudnotes-backend"
    DOCKER_IMAGE_FE  = "your-username/cloudnotes-frontend"
    IMAGE_TAG        = "${env.BUILD_NUMBER}"
    KUBECONFIG       = credentials('kubeconfig')
  }

  stages {

    stage('Checkout') {
      steps {
        git branch: 'main',
            url: 'https://github.com/your-username/cloudnotes.git'
        echo "Code checked out at commit: ${env.GIT_COMMIT}"
      }
    }

    stage('Security Scan') {
      steps {
        sh 'pip install truffleHog'
        sh 'trufflehog filesystem . --only-verified || true'
        echo "Secret scan complete"
      }
    }

    stage('Run Tests') {
      steps {
        dir('app/backend') {
          sh 'pip install -r requirements.txt'
          sh 'python -m pytest tests/ -v --tb=short'
        }
      }
      post {
        always {
          junit 'app/backend/tests/results.xml'
        }
      }
    }

    stage('Build Docker Images') {
      steps {
        sh "docker build -t ${DOCKER_IMAGE_BE}:${IMAGE_TAG} ./app/backend"
        sh "docker build -t ${DOCKER_IMAGE_FE}:${IMAGE_TAG} ./app/frontend"
        echo "Images built: tag = ${IMAGE_TAG}"
      }
    }

    stage('Push to Docker Hub') {
      steps {
        sh "echo ${DOCKERHUB_CREDS_PSW} | docker login -u ${DOCKERHUB_CREDS_USR} --password-stdin"
        sh "docker push ${DOCKER_IMAGE_BE}:${IMAGE_TAG}"
        sh "docker push ${DOCKER_IMAGE_FE}:${IMAGE_TAG}"
        sh "docker push ${DOCKER_IMAGE_BE}:latest"
        sh "docker push ${DOCKER_IMAGE_FE}:latest"
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        sh """
          kubectl set image deployment/backend \
            backend=${DOCKER_IMAGE_BE}:${IMAGE_TAG} \
            -n cloudnotes --kubeconfig=${KUBECONFIG}

          kubectl set image deployment/frontend \
            frontend=${DOCKER_IMAGE_FE}:${IMAGE_TAG} \
            -n cloudnotes --kubeconfig=${KUBECONFIG}

          kubectl rollout status deployment/backend -n cloudnotes
          kubectl rollout status deployment/frontend -n cloudnotes
        """
      }
    }

    stage('Smoke Test') {
      steps {
        sh """
          sleep 10
          curl -f http://<APP-IP>/api/health || exit 1
          echo "Smoke test passed!"
        """
      }
    }

  }

  post {
    success {
      echo "Pipeline SUCCESS — Build #${env.BUILD_NUMBER} deployed"
    }
    failure {
      echo "Pipeline FAILED — Check logs for Build #${env.BUILD_NUMBER}"
    }
  }
}
```

**4.3 — GitHub Webhook Setup**
1. Go to GitHub Repo → Settings → Webhooks → Add Webhook
2. Payload URL: `http://<JENKINS-IP>:8080/github-webhook/`
3. Content type: `application/json`
4. Events: `Just the push event`

Now every `git push` to `main` automatically triggers the pipeline.

**Key Concepts Demonstrated:**
- CI/CD pipeline stages and methodologies
- Jenkins declarative pipeline syntax
- Automated testing in the pipeline
- Docker image build and registry push
- Rolling deployments to Kubernetes
- Webhook-based pipeline triggers

---

### UNIT V — Monitoring, Observability, and Security

**Goal:** Add full observability and secure the pipeline and infrastructure.

#### Tasks

**5.1 — Add Prometheus Metrics to Flask App**
```python
# In app.py, add these lines
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Custom metrics
notes_created = metrics.counter(
    'notes_created_total',
    'Total number of notes created'
)
notes_deleted = metrics.counter(
    'notes_deleted_total',
    'Total number of notes deleted'
)
```

**5.2 — Prometheus Configuration**
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'cloudnotes-backend'
    static_configs:
      - targets: ['backend-service:5000']
    metrics_path: '/metrics'

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
```

**5.3 — Alert Rules**
```yaml
# monitoring/prometheus/alert_rules.yml
groups:
  - name: cloudnotes_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(flask_http_request_total{status="500"}[5m]) > 0.1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on CloudNotes backend"

      - alert: PodDown
        expr: up{job="cloudnotes-backend"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "CloudNotes backend pod is down"
```

**5.4 — Grafana Dashboard**
Deploy Grafana and create panels for:
- HTTP requests per second (rate over 5 minutes)
- Notes created over time (counter graph)
- Response time (P50, P90, P99 percentiles)
- Error rate percentage
- Pod CPU and memory usage

**5.5 — Run the Monitoring Stack**
```bash
# Add to docker-compose or as K8s deployments
docker run -d -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus:/etc/prometheus \
  prom/prometheus

docker run -d -p 3000:3000 \
  -v $(pwd)/monitoring/grafana:/etc/grafana/provisioning \
  grafana/grafana

# Access:
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
```

**5.6 — IAM Security Setup (AWS)**
```json
// Minimal IAM policy for Jenkins (least privilege principle)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage"
      ],
      "Resource": "*"
    }
  ]
}
```

**5.7 — Secrets Scan in Pipeline**
```bash
# Already included in Jenkinsfile Stage 2
pip install truffleHog
trufflehog filesystem . --only-verified
```

**5.8 — Kubernetes RBAC**
```yaml
# kubernetes/rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: cloudnotes
  name: cloudnotes-role
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cloudnotes-binding
  namespace: cloudnotes
subjects:
  - kind: ServiceAccount
    name: jenkins-sa
roleRef:
  kind: Role
  name: cloudnotes-role
  apiGroup: rbac.authorization.k8s.io
```

**Key Concepts Demonstrated:**
- Prometheus scraping and PromQL queries
- Grafana dashboards and alert panels
- AWS IAM, least privilege, shared responsibility model
- DevSecOps: secrets scanning in CI pipeline
- Kubernetes RBAC for access control
- Securing CI/CD pipelines

---

## 5. Step-by-Step Build Guide

### Phase 1 — Local App (Week 1)
```
Day 1:  Set up GitHub repo, branching strategy, write README
Day 2:  Build Flask backend (CRUD API for notes)
Day 3:  Build HTML/JS frontend
Day 4:  Write unit tests (pytest)
Day 5:  Dockerize backend and frontend, test with docker-compose
```

### Phase 2 — Cloud & IaC (Week 2)
```
Day 6:  Write Terraform scripts (VPC, EC2, S3)
Day 7:  Deploy Terraform to AWS Free Tier
Day 8:  Write Kubernetes manifests (deployment, service, PVC)
Day 9:  Deploy to Minikube locally
Day 10: Verify K8s rollouts and pod health
```

### Phase 3 — CI/CD Pipeline (Week 3)
```
Day 11: Set up Jenkins in Docker
Day 12: Write Jenkinsfile with all 6 stages
Day 13: Configure Docker Hub credentials in Jenkins
Day 14: Set up GitHub webhook
Day 15: End-to-end test: git push → auto-deploy
```

### Phase 4 — Monitoring & Security (Week 4)
```
Day 16: Add Prometheus metrics to Flask app
Day 17: Configure Prometheus scrape config
Day 18: Set up Grafana, create dashboard panels
Day 19: Configure IAM roles, RBAC, secrets scan
Day 20: Final testing, documentation, demo prep
```

---

## 6. Starter Code & Config Files

### Flask Backend (app/backend/app.py)
```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///notes.db'
)
db = SQLAlchemy(app)
metrics = PrometheusMetrics(app)

class Note(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body  = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    return jsonify([{"id": n.id, "title": n.title, "body": n.body}
                    for n in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    note = Note(title=data['title'], body=data['body'])
    db.session.add(note)
    db.session.commit()
    return jsonify({"id": note.id, "message": "Note created"}), 201

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Backend Requirements (app/backend/requirements.txt)
```
flask==3.0.0
flask-sqlalchemy==3.1.1
psycopg2-binary==2.9.9
prometheus-flask-exporter==0.23.0
pytest==7.4.3
```

### Kubernetes Backend Deployment (kubernetes/backend-deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: cloudnotes
  labels:
    app: backend
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
          image: your-username/cloudnotes-backend:latest
          ports:
            - containerPort: 5000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: database-url
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /api/health
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 10
```

### .gitignore
```
# Python
__pycache__/
*.pyc
*.pyo
.env
venv/
*.egg-info/

# Terraform
*.tfstate
*.tfstate.backup
.terraform/
*.tfvars

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db

# Secrets (NEVER commit these)
*.pem
*.key
secrets.yaml
```

---

## 7. Timeline / Sprint Plan

```
WEEK 1 — Foundation
  ✅ GitHub repo setup with branches
  ✅ Flask backend with CRUD API
  ✅ HTML/JS frontend
  ✅ Unit tests with pytest
  ✅ Dockerfiles + docker-compose

WEEK 2 — Cloud & Infrastructure
  ✅ AWS Free Tier account setup
  ✅ Terraform: VPC, EC2, S3
  ✅ Kubernetes manifests (all YAML files)
  ✅ Minikube local deployment
  ✅ Push images to Docker Hub

WEEK 3 — CI/CD Pipeline
  ✅ Jenkins setup in Docker
  ✅ Jenkinsfile with 6 stages
  ✅ Docker Hub credentials in Jenkins
  ✅ GitHub webhook configured
  ✅ Full end-to-end pipeline test

WEEK 4 — Monitoring & Security
  ✅ Prometheus metrics in Flask app
  ✅ Prometheus scrape config
  ✅ Grafana dashboard (4 panels)
  ✅ IAM policy + K8s RBAC
  ✅ Secrets scan in Jenkins pipeline
  ✅ Documentation + demo prep
```

---

## 8. Tools & Free Resources

| Tool | Purpose | Cost |
|------|---------|------|
| GitHub | Source control | Free |
| AWS Free Tier | EC2, S3, Lambda | Free (12 months) |
| Docker Hub | Container registry | Free (public repos) |
| Minikube | Local Kubernetes | Free |
| Jenkins | CI/CD server | Free (open source) |
| Terraform | IaC provisioning | Free (open source) |
| Prometheus | Metrics collection | Free (open source) |
| Grafana | Metrics visualization | Free (open source) |
| Flask | Backend framework | Free |
| PostgreSQL | Database | Free |

**Useful Learning Links:**
- Terraform docs: https://developer.hashicorp.com/terraform/docs
- Kubernetes: https://kubernetes.io/docs/tutorials/
- Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/
- Prometheus: https://prometheus.io/docs/introduction/overview/
- Grafana: https://grafana.com/docs/grafana/latest/

---

## 9. Evaluation Checklist

Use this checklist for your final demo:

### Unit I
- [ ] GitHub repo with main/dev/feature branches exists
- [ ] At least 10 meaningful commits with clear messages
- [ ] README documents cloud delivery models (IaaS/PaaS/SaaS)
- [ ] App manually deployed on AWS EC2 (public cloud)

### Unit II
- [ ] Backend Dockerfile builds and runs correctly
- [ ] Frontend Dockerfile builds and serves via Nginx
- [ ] `docker-compose up` starts all 3 services (frontend, backend, db)
- [ ] Kubernetes: all pods are Running in `cloudnotes` namespace
- [ ] K8s: services are accessible via `minikube service`

### Unit III
- [ ] `terraform plan` shows expected resources
- [ ] `terraform apply` creates VPC, EC2, S3 on AWS
- [ ] Terraform state file is tracked (or remote state configured)
- [ ] Cloud cost estimate documented in README

### Unit IV
- [ ] Jenkins pipeline visible at http://<IP>:8080
- [ ] All 6 stages pass (Checkout → Scan → Test → Build → Push → Deploy)
- [ ] `git push` triggers the pipeline automatically via webhook
- [ ] Docker Hub shows newly pushed image tags after each build

### Unit V
- [ ] `/metrics` endpoint on Flask returns Prometheus data
- [ ] Prometheus at :9090 shows `notes_created_total` metric
- [ ] Grafana at :3000 shows at least 3 working dashboard panels
- [ ] AWS IAM role with least-privilege policy assigned to Jenkins
- [ ] Pipeline includes truffleHog secrets scan stage

---

*Project: CloudNotes | Course: Cloud and DevOps Fundamentals | All 5 Units Covered*
# 📋 Final Project Report: CloudNotes DevOps Lifecycle
**Date:** May 19, 2026  
**Project Owner:** Savinay Singh  
**Status:** 100% Complete & Verified  

---

## 1. Project Overview
CloudNotes is a production-grade, multi-tier web application designed to demonstrate the complete DevOps lifecycle. The project maps directly to the 5 units of the Cloud & DevOps syllabus, transitioning from a local Flask app to a fully automated, cloud-hosted, and monitored ecosystem.

---

## 2. Chronological Implementation Steps

### Phase 1: Local Development & Containerization (Unit I & II)
*   **Scaffolding:** Created a professional directory structure including `app/`, `docker/`, `kubernetes/`, `terraform/`, and `jenkins/`.
*   **Backend:** Implemented a Flask REST API with SQLAlchemy and integrated Prometheus metrics.
*   **Frontend:** Built a responsive HTML/JS UI served via Nginx with an API proxy.
*   **Dockerization:** Wrote multi-stage Dockerfiles for both tiers and a `docker-compose.yml` for local orchestration.
*   **Validation:** Verified the full stack locally with database persistence and REST API health checks.

### Phase 2: Orchestration with Kubernetes (Unit II)
*   **Cluster Setup:** Initialized a local Kubernetes cluster using Minikube (Docker driver).
*   **Manifests:** Wrote and applied K8s YAML files for:
    *   **Deployments:** Scalable replicas for Backend and Frontend.
    *   **Services:** Load balancing via ClusterIP and NodePort.
    *   **Persistence:** PersistentVolumeClaims (PVC) for the Postgres database.
    *   **Security:** Kubernetes Secrets for database credentials.
*   **Verification:** Confirmed all pods were `Running` and the service was reachable via Minikube tunnel.

### Phase 3: Infrastructure as Code on AWS (Unit III)
*   **Terraform Modules:** Developed a modular IaC project to provision:
    *   **Networking:** VPC, Public Subnets, Internet Gateway, and Route Tables.
    *   **Security:** Security Groups with specific rules for SSH (22), HTTP (80/8080), and Ping (ICMP).
    *   **Compute:** Two EC2 instances (t3.micro) for Production and CI/CD.
    *   **Storage:** S3 bucket for static asset backups.
*   **Automation:** Injected `user_data` startup scripts to automatically install Docker and Jenkins upon server launch.

### Phase 4: Continuous Integration & Deployment (Unit IV)
*   **Jenkins Setup:** Launched a Jenkins server on AWS and configured the initial security credentials.
*   **Pipeline Development:** Wrote a declarative `Jenkinsfile` featuring:
    *   **Stage 1: Checkout:** Automated code pull from GitHub.
    *   **Stage 2: Build:** Creation of Docker images with dynamic tagging.
    *   **Stage 3: Testing:** Running Pytest *inside* a Docker container (Container-Native Testing).
    *   **Stage 4: Delivery:** Automated push to Docker Hub (`savinaysingh7`).
    *   **Stage 5: Deployment:** Secure SSH-based Continuous Deployment to the AWS App server.
*   **Success:** Achieved a 100% "Green" pipeline status.

### Phase 5: Monitoring & Observability (Unit V)
*   **Instrumentation:** Added custom Prometheus counters (`notes_created_total`) to the Flask source code.
*   **Scraping:** Configured Prometheus to pull real-time metrics from the running containers.
*   **Visualization:** Created a custom Grafana Dashboard with panels for Request Rate and Application Health.
*   **Verification:** Verified live data flow by creating notes and observing graph spikes in Grafana.

---

## 3. Final Architecture Summary
*   **Source Control:** [https://github.com/savinaysingh7/cloudnotes](https://github.com/savinaysingh7/cloudnotes)
*   **Compute:** AWS EC2 (Ubuntu 22.04 LTS)
*   **CI/CD:** Jenkins (AWS Hosted)
*   **Images:** Docker Hub (Public)
*   **Monitoring:** Prometheus + Grafana (Local/Docker)

---

## 4. Key Technical Challenges Resolved
1.  **Race Condition:** Added database health checks in Docker Compose to prevent backend crashes on startup.
2.  **Environment Mismatch:** Resolved "Docker not found" in Jenkins by implementing binary bridging and explicit pathing.
3.  **Cross-Platform Keys:** Fixed "libcrypto" errors by sanitizing SSH private keys to remove Windows line endings.
4.  **Import Logic:** Fixed Python `ModuleNotFoundError` by correctly configuring `PYTHONPATH` within the Jenkins test container.

---
**Report compiled by Gemini CLI on behalf of Savinay Singh.**

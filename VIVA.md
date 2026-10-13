# 🎓 CloudNotes Project VIVA - INT378: Advancements in Cloud and DevOps

This document contains VIVA questions and answers based on the CloudNotes project and its alignment with the current course.

---

## 📦 Unit II: Containerization & Orchestration (Docker & Kubernetes)

**Q1: What is the difference between a Docker Image and a Docker Container?**
*   **Answer:** An **Image** is a read-only template (a blueprint) containing the application code, libraries, and dependencies. A **Container** is a running instance of that image. You can run multiple containers from a single image.

**Q2: How are the frontend and backend packaged?**
*   **Answer:** They have separate Dockerfiles and images. The Nginx image serves the static frontend and proxies API requests; the Python image runs the Flask backend with Gunicorn. The database is a separate PostgreSQL service.

**Q3: What is the role of `docker-compose`?**
*   **Answer:** It is a tool for defining and running multi-container Docker applications. We use a YAML file (`docker-compose.yml`) to configure our app's services (frontend, backend, database, monitoring) and start them all with a single command.

**Q4: What is a Kubernetes Pod?**
*   **Answer:** A Pod is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster and can contain one or more containers (like our Flask backend).

**Q5: Why do we use Kubernetes Services?**
*   **Answer:** Pods are ephemeral and may be replaced with new IP addresses. A Service provides a stable name and virtual IP for selected pods and distributes connections among its endpoints.

**Q6: How does this project scale Kubernetes workloads?**
*   **Answer:** KEDA ScaledObjects in `kubernetes/hpa.yaml` query Prometheus for the Flask HTTP request rate. The backend scales between 2 and 5 replicas; the frontend between 2 and 4. This is horizontal pod scaling based on API traffic. It is distinct from vertical scaling, which changes CPU or memory allocated to a pod.

---

## 🏗️ Unit III: Infrastructure as Code (Terraform & AWS)

**Q7: What is Infrastructure as Code (IaC)?**
*   **Answer:** IaC is the process of managing and provisioning computing infrastructure through machine-readable definition files (like Terraform `.tf` files) rather than physical hardware configuration or interactive configuration tools.

**Q8: What is the purpose of the `terraform.tfstate` file?**
*   **Answer:** Terraform uses this local state file to map real-world resources to your configuration. It keeps track of metadata and helps Terraform determine what changes to make when you run `apply`.

**Q9: Explain the modular approach in your Terraform code.**
*   **Answer:** We split our infrastructure into logical modules (VPC, EC2, S3). This makes the code reusable, easier to maintain, and organized.

**Q10: What is an AWS Security Group?**
*   **Answer:** It is a stateful virtual firewall attached to network interfaces. This demo defines ingress for web and administration/monitoring ports; its broad public rules must be restricted before any production use.

---

## 🔄 Unit IV: CI/CD Pipeline (Jenkins)

**Q11: What is CI/CD?**
*   **Answer:** **Continuous Integration (CI)** is the practice of automating the integration of code changes from multiple contributors into a single software project. **Continuous Deployment (CD)** automates the delivery of that code to production environments.

**Q12: What is a `Jenkinsfile`?**
*   **Answer:** It is a text file that contains the definition of a Jenkins Pipeline and is checked into source control. It implements "Pipeline as Code."

**Q13: Describe the stages in your Jenkins pipeline.**
*   **Answer:** 
    1. **Checkout:** Pulling code from GitHub.
    2. **Backend tests:** Build a backend image and run pytest.
    3. **Secret scan:** Run TruffleHog for verified secrets.
    4. **Image build and scan:** Build versioned images and run Trivy (the current Jenkinsfile scan is non-blocking).
    5. **Publish and deploy:** Push Docker Hub tags, then SSH to the app host to apply Kubernetes manifests, set build-tagged images, and check rollouts/health.

---

## 📊 Unit V: Monitoring & Security

**Q14: How does Prometheus collect metrics from the application?**
*   **Answer:** Prometheus uses a "pull model." It scrapes (fetches) metrics from the `/metrics` endpoint of our Flask application at regular intervals.

**Q15: What is the role of Grafana in this project?**
*   **Answer:** In the Docker Compose environment, Grafana connects to Prometheus and displays the provisioned dashboard, including backend status, note operation counters, request rate, errors, latency, and memory metrics. The Kubernetes manifests deploy Prometheus and alert rules, but do not deploy Grafana.

**Q16: What is DevSecOps?**
*   **Answer:** It stands for Development, Security, and Operations. It’s an approach to culture, automation, and platform design that integrates security as a shared responsibility throughout the entire IT lifecycle. We implemented this using Trivy (vulnerability scanning) and TruffleHog (secret scanning) in our pipeline.

---

## 🚀 Bonus Section: Production Readiness (To impress the examiner)

**Q17: If you were to deploy this project for a real enterprise company, what security improvements would you make?**
*   **Answer:** For a true production environment, I would make three major security changes:
    1.  **Restrict Security Groups:** Some inbound rules allow `0.0.0.0/0`; I would allow only required traffic from a load balancer, VPN, or trusted administration addresses.
    2.  **Remove Root Access:** I would ensure Jenkins and application containers run with least privilege and non-root identities where supported.
    3.  **Secret Management:** Instead of injecting credentials via Groovy scripts or `.env` files, I would integrate a proper secrets manager like AWS Secrets Manager or HashiCorp Vault.

**Q18: How would you improve the CI/CD Pipeline for scale?**
*   **Answer:** 
    1.  **Stop Committing Dynamic State:** Currently, our automation scripts write the new App IP directly into the `Jenkinsfile` and commit it. In a real environment, I would pass the IP as a runtime parameter or use AWS Systems Manager (SSM) Parameter Store to decouple code from infrastructure state.
    2.  **Blocking Scans:** I would configure our Trivy vulnerability scans to *fail* the build (exit code 1) if a CRITICAL vulnerability is found, rather than just printing a warning.
    3.  **Immutable Tags:** I would stop using the `latest` tag for Docker images in production, as it makes rollbacks difficult. I would pin deployments to specific commit hashes or build numbers.

---
*Created for CloudNotes Project VIVA Preparation.*

# 🎓 CloudNotes Project VIVA - Questions & Answers

This document contains a comprehensive list of potential VIVA questions and detailed answers based on the CloudNotes DevOps project.

---

## 📦 Unit II: Containerization & Orchestration (Docker & Kubernetes)

**Q1: What is the difference between a Docker Image and a Docker Container?**
*   **Answer:** An **Image** is a read-only template (a blueprint) containing the application code, libraries, and dependencies. A **Container** is a running instance of that image. You can run multiple containers from a single image.

**Q2: Explain the multi-stage build used in this project.**
*   **Answer:** Multi-stage builds (seen in our Dockerfiles) allow us to use one stage for building/compiling the app and a second, smaller stage for running it. This keeps the final production image size small and secure by excluding build tools and source code.

**Q3: What is the role of `docker-compose`?**
*   **Answer:** It is a tool for defining and running multi-container Docker applications. We use a YAML file (`docker-compose.yml`) to configure our app's services (frontend, backend, database, monitoring) and start them all with a single command.

**Q4: What is a Kubernetes Pod?**
*   **Answer:** A Pod is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster and can contain one or more containers (like our Flask backend).

**Q5: Why do we use Kubernetes Services?**
*   **Answer:** Pods are ephemeral (they can die and get replaced with new IPs). A **Service** provides a stable IP address and DNS name to access a set of Pods, acting as a load balancer.

---

## 🏗️ Unit III: Infrastructure as Code (Terraform & AWS)

**Q6: What is Infrastructure as Code (IaC)?**
*   **Answer:** IaC is the process of managing and provisioning computing infrastructure through machine-readable definition files (like Terraform `.tf` files) rather than physical hardware configuration or interactive configuration tools.

**Q7: What is the purpose of the `terraform.tfstate` file?**
*   **Answer:** Terraform uses this local state file to map real-world resources to your configuration. It keeps track of metadata and helps Terraform determine what changes to make when you run `apply`.

**Q8: Explain the "Modular" approach in your Terraform code.**
*   **Answer:** We split our infrastructure into logical modules (VPC, EC2, S3). This makes the code reusable, easier to maintain, and organized.

**Q9: What is an AWS Security Group?**
*   **Answer:** It acts as a virtual firewall for your EC2 instances to control inbound and outbound traffic. In this project, we opened port 80 (App), 8080 (Jenkins), and 22 (SSH).

---

## 🔄 Unit IV: CI/CD Pipeline (Jenkins)

**Q10: What is CI/CD?**
*   **Answer:** **Continuous Integration (CI)** is the practice of automating the integration of code changes from multiple contributors into a single software project. **Continuous Deployment (CD)** automates the delivery of that code to production environments.

**Q11: What is a `Jenkinsfile`?**
*   **Answer:** It is a text file that contains the definition of a Jenkins Pipeline and is checked into source control. It implements "Pipeline as Code."

**Q12: Describe the stages in your Jenkins pipeline.**
*   **Answer:** 
    1. **Checkout:** Pulling code from GitHub.
    2. **Security Scan:** Checking for secrets/vulnerabilities.
    3. **Test:** Running Pytest for the backend.
    4. **Build & Push:** Creating Docker images and pushing to Docker Hub.
    5. **Deploy:** SSH-ing into the AWS server and updating the containers.

---

## 📊 Unit V: Monitoring & Security

**Q13: How does Prometheus collect metrics from the application?**
*   **Answer:** Prometheus uses a "pull model." It scrapes (fetches) metrics from the `/metrics` endpoint of our Flask application at regular intervals.

**Q14: What is the role of Grafana in this project?**
*   **Answer:** Grafana is the visualization layer. It connects to Prometheus as a data source and displays the metrics (like request rates, CPU usage, note count) on a user-friendly dashboard.

**Q15: What is "DevSecOps"?**
*   **Answer:** It stands for Development, Security, and Operations. It’s an approach to culture, automation, and platform design that integrates security as a shared responsibility throughout the entire IT lifecycle. We implemented this using Trivy (vulnerability scanning) and TruffleHog (secret scanning) in our pipeline.

---

## 🚀 Bonus Section: Production Readiness (To impress the examiner)

**Q16: If you were to deploy this project for a real enterprise company, what security improvements would you make?**
*   **Answer:** For a true production environment, I would make three major security changes:
    1.  **Restrict Security Groups:** Currently, ports are open to the world (`0.0.0.0/0`) for ease of demonstration. I would lock these down to allow traffic only from a Load Balancer or a specific VPN.
    2.  **Remove Root Access:** I would ensure Jenkins and the Flask containers run as non-root users to minimize the blast radius if a container is compromised.
    3.  **Secret Management:** Instead of injecting credentials via Groovy scripts or `.env` files, I would integrate a proper secrets manager like AWS Secrets Manager or HashiCorp Vault.

**Q17: How would you improve the CI/CD Pipeline for scale?**
*   **Answer:** 
    1.  **Stop Committing Dynamic State:** Currently, our automation scripts write the new App IP directly into the `Jenkinsfile` and commit it. In a real environment, I would pass the IP as a runtime parameter or use AWS Systems Manager (SSM) Parameter Store to decouple code from infrastructure state.
    2.  **Blocking Scans:** I would configure our Trivy vulnerability scans to *fail* the build (exit code 1) if a CRITICAL vulnerability is found, rather than just printing a warning.
    3.  **Immutable Tags:** I would stop using the `latest` tag for Docker images in production, as it makes rollbacks difficult. I would pin deployments to specific commit hashes or build numbers.

---
*Created for CloudNotes Project VIVA Preparation.*

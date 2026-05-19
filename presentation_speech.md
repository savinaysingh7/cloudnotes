# CloudNotes — Presentation Speech Script
### ~12 minutes | 10 Slides | Savinay Singh

> [!TIP]
> **How to use this script:**
> - Read it naturally, don't memorize word-for-word
> - `[NEXT SLIDE]` = click to advance
> - `[PAUSE]` = take a breath, let the visual sink in
> - `[POINT]` = gesture at the slide
> - Speak slowly on technical terms, faster on transitions

---

## Slide 1 — Title

> Good morning everyone. My name is Savinay Singh, and today I'll be presenting **CloudNotes** — a containerized note-taking application built with a complete DevOps pipeline.
>
> Now, before you think "it's just a notes app" — that's actually the whole point. The app is intentionally simple. What makes this project interesting is everything *around* the app — the containers, the cloud infrastructure, the automated pipeline, and the monitoring. That's where all the learning happened.

`[NEXT SLIDE]`

---

## Slide 2 — Project Overview & Unit Mapping

> So what did we actually build? [POINT at the left illustration]
>
> CloudNotes is a basic CRUD application — you can create a note, read your notes, and delete them. It has a Flask backend, an Nginx frontend, and a PostgreSQL database. Simple.
>
> But look at the right side. [POINT at the unit mapping]
>
> Every single unit of our syllabus is covered through this one project:
>
> - **Unit I** — we set up a proper GitHub repository with three branches and deployed on AWS EC2.
> - **Unit II** — we containerized everything with Docker — five services running together — and deployed on Kubernetes using Minikube.
> - **Unit III** — we wrote Terraform scripts that automatically provision our entire AWS infrastructure — VPC, two EC2 instances, and an S3 bucket.
> - **Unit IV** — we built a five-stage Jenkins pipeline that automatically builds, tests, and deploys the app.
> - **Unit V** — we added Prometheus for metrics collection, Grafana for visualization, and proper security with AWS Security Groups.
>
> Everything has been implemented and verified. [PAUSE] Let me show you how it all fits together.

`[NEXT SLIDE]`

---

## Slide 3 — System Architecture

> This is the complete architecture of our project — as it was actually built and deployed. [PAUSE]
>
> Let me walk you through the flow. [POINT at the top]
>
> It starts with me, the developer. I write code and push it to **GitHub**. GitHub sends a **webhook** to our Jenkins server, which is running on an AWS EC2 instance.
>
> Jenkins then runs our **five-stage pipeline** — it checks out the code, builds Docker images for both the backend and frontend, runs our pytest tests *inside* the Docker container, pushes the images to Docker Hub under my account `savinaysingh7`, and finally **SSHs into the production server** and deploys the new version.
>
> On the App Server [POINT], we have three containers running on a Docker bridge network — Nginx serving the frontend on port 80, Flask running the backend API on port 5000, and PostgreSQL as our database.
>
> And then there's the monitoring layer [POINT at bottom-right] — Prometheus scrapes metrics from the backend every 15 seconds, and Grafana visualizes them on a dashboard.
>
> The key thing here is — this is all **live**. This is not a diagram of what we planned, this is what's actually running.

`[NEXT SLIDE]`

---

## Slide 4 — Unit I: Git & Cloud Fundamentals

> Starting with Unit I — Git and Cloud Fundamentals.
>
> On the left [POINT], you can see our actual branching strategy. We used three branches — `main` for production-ready code, `dev` for integration, and `feature/initial-scaffold` for the initial development work.
>
> Over the course of the project, we made **10 meaningful commits** — from the initial scaffold, to automated cloud deployment, pipeline fixes, and the final master resolution. Every commit tells a story of the project evolving.
>
> The entire codebase is hosted on GitHub at `github.com/savinaysingh7/cloudnotes`.
>
> On the right side [POINT], we mapped our project to the three cloud delivery models:
> - **IaaS** — our EC2 instances are Infrastructure as a Service. We manage the OS, install Docker, deploy our app ourselves.
> - **PaaS** — something like Elastic Beanstalk where the platform handles deployment for you.
> - **SaaS** — GitHub itself, Docker Hub — these are services we just use without managing any infrastructure.

`[NEXT SLIDE]`

---

## Slide 5 — Unit II: Docker & Kubernetes

> Unit II was about containerization and orchestration. [PAUSE]
>
> On the left — **Containerization**. [POINT]
>
> We wrote two Dockerfiles. The backend uses `python:3.11-slim` as the base image and runs our Flask app on port 5000. The frontend uses `nginx:alpine` with a custom `nginx.conf` that reverse-proxies API requests to the backend — so the user just hits port 80 and everything routes correctly.
>
> Our `docker-compose.yml` brings up **five services** — the frontend, backend, PostgreSQL, Prometheus, and Grafana — all connected on a single Docker bridge network called `cloudnotes-network`. We also added health checks so the backend waits for the database to be ready before starting.
>
> All images are pushed to Docker Hub under `savinaysingh7`.
>
> On the right — **Kubernetes**. [POINT]
>
> We wrote six manifest files and deployed everything on Minikube. The backend runs with **two replicas** and has a **liveness probe** hitting `/api/health` to ensure pods are healthy. PostgreSQL has a **PersistentVolumeClaim** so data survives pod restarts, and database credentials are stored in a **Kubernetes Secret** — not hardcoded.

`[NEXT SLIDE]`

---

## Slide 6 — Unit III: Terraform & AWS Infrastructure

> Unit III — this is where we moved from local development to the real cloud. [PAUSE]
>
> We wrote a **modular Terraform project**. [POINT at the module tree]
>
> The root `main.tf` calls four components — an SSH key pair, and three modules: `vpc` for networking, `ec2` for compute — which we use twice — and `s3` for storage.
>
> The VPC module creates a full network with public subnets, an internet gateway, route tables, and security groups that only allow ports 22, 80, and 8080.
>
> The EC2 module is reused for two servers — one for Jenkins, one for the application. Both are `t3.micro` instances — that's **AWS Free Tier**, so the total cost is zero.
>
> Now here's the interesting part [POINT at the server cards] — both servers **configure themselves** on launch using `user_data` scripts. The Jenkins server automatically installs Docker, Java, and Jenkins. The App server installs Docker Compose, pulls our images from Docker Hub, and starts the entire application. Zero manual SSH needed for the initial setup.
>
> At the bottom [POINT], you can see the Terraform workflow we followed — `init`, `plan`, `apply` — and it provisioned the VPC, two EC2 instances, and an S3 bucket.

`[NEXT SLIDE]`

---

## Slide 7 — Unit IV: CI/CD Pipeline

> This is probably the most exciting slide. [PAUSE]
>
> Our Jenkins pipeline has **five stages**, and all of them pass. [POINT at each stage]
>
> **Stage 1 — Checkout**: Jenkins pulls the latest code from GitHub.
>
> **Stage 2 — Build**: Docker images are built for both the backend and the frontend, tagged with the Jenkins build number.
>
> **Stage 3 — Test**: And this is something I'm proud of — we run our tests **inside the Docker container itself**. The command is `docker run --rm` with `PYTHONPATH` set, running pytest. This guarantees that tests run in the *exact same environment* that gets deployed. No "works on my machine" problems.
>
> **Stage 4 — Push**: Images are pushed to Docker Hub with both the build number tag and the `latest` tag, using Jenkins credential binding for security.
>
> **Stage 5 — Deploy**: Jenkins SSHs into the production server, pulls the new images, stops the old containers, and starts fresh ones. This is **real continuous deployment** — every successful pipeline run updates the live application.
>
> And at the bottom [POINT] — Pipeline Successful. The production app was live and updated at that IP address.

`[NEXT SLIDE]`

---

## Slide 8 — Unit V: Monitoring & Security

> Unit V covers two things — observability and security. [PAUSE]
>
> On the **observability** side [POINT left]:
>
> We instrumented our Flask application with **custom Prometheus counters** — `notes_created_total` and `notes_deleted_total`. These are exposed at a `/metrics` endpoint that Prometheus scrapes every 15 seconds.
>
> The data flows from Flask to Prometheus on port 9091, and then into Grafana on port 3001 where we built a dashboard with panels for request rate, total notes created, and backend health status.
>
> We verified this end-to-end — we created notes through the UI and watched the graphs spike in real time on Grafana.
>
> On the **security** side [POINT right]:
>
> We implemented three layers of security. The outermost layer is **AWS Security Groups** — only ports 22, 80, and 8080 are open, everything else is blocked. The middle layer is **Kubernetes Secrets** — database credentials are base64 encoded and injected via `secretKeyRef`, never hardcoded. The innermost layer is **Jenkins Credentials** — Docker Hub passwords are handled through the `withCredentials` block, never exposed in console logs.

`[NEXT SLIDE]`

---

## Slide 9 — Challenges & Results

> No real project is without challenges, and I want to be transparent about the ones we faced. [PAUSE]
>
> [POINT at the challenge strips]
>
> **Challenge 1** — Jenkins couldn't find Docker. Solution: we mounted the Docker binary from the host into the Jenkins container.
>
> **Challenge 2** — Permission denied on the Docker socket. Solution: we relaunched Jenkins as the root user.
>
> **Challenge 3** — SSH connections from Jenkins to the app server were failing with a `libcrypto` error. Turns out the SSH keys had Windows-style line endings. We sanitized the keys and it worked.
>
> **Challenge 4** — Pytest was throwing `ModuleNotFoundError` inside the container. We fixed it by setting `PYTHONPATH=.` in the test command.
>
> Each of these bugs actually deepened my understanding of how containers, permissions, and cross-platform tooling work.
>
> And now the results. [POINT at the bottom cards]
>
> The production app is **live** at `44.220.170.36`. Jenkins has **all five stages green**. Docker Hub has multiple tagged versions of both images. And Grafana is serving real-time metrics. The full codebase is on GitHub — 10 commits across 3 branches.

`[NEXT SLIDE]`

---

## Slide 10 — Thank You

> So to summarize — CloudNotes is a small app, but it touches every part of the DevOps lifecycle. From Git branching to Docker containers, Kubernetes orchestration, Terraform infrastructure, Jenkins automation, and Prometheus monitoring — all working together as one system.
>
> The total cost of running this entire project is **zero rupees** thanks to AWS Free Tier and open-source tooling.
>
> [PAUSE]
>
> Thank you. I'm happy to take any questions.

---

> [!IMPORTANT]
> **Quick Tips for Delivery:**
> - **Don't read the script** — know the flow, speak naturally
> - **Point at the slide** when referencing visuals — it guides the audience's eyes
> - **Slow down** on the Architecture (Slide 3) and Pipeline (Slide 7) slides — those are your star slides
> - **Make eye contact** during the Challenges slide — it shows confidence
> - **Time yourself** — aim for 10-12 minutes, leaving 2-3 minutes for Q&A
> - If asked "what would you do differently?" → mention adding Kubernetes in production instead of Docker Compose, or adding a staging environment

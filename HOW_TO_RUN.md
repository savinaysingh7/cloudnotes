# CloudNotes: setup and deployment guide

This guide describes the repository's local Compose, Kubernetes, and AWS workflows. Run cloud infrastructure commands only in an AWS account you control and review the Terraform plan and expected costs first.

## Requirements

- Docker Desktop or Docker Engine with Compose
- For Kubernetes: `kubectl`, Minikube (or another cluster), an ingress controller, and KEDA for the traffic-based `ScaledObject` resources
- For AWS: Terraform, AWS credentials, a valid provisioning SSH key supplied as `ssh_public_key`, and a dedicated Jenkins deploy key pair
- For CI/CD: a Jenkins host configured from `jenkins/jenkins.yaml`, Docker Hub credentials, an SSH key credential for the app host, and a GitHub webhook to Jenkins

## Local development with Docker Compose

1. Copy `docker/.env.example` to `docker/.env` and replace every `CHANGE_ME` placeholder. Do not commit `docker/.env`.
   Set `POSTGRES_PASSWORD` and the password portion of `DATABASE_URL` to the same value. The URL format is `postgresql+psycopg2://admin:<password>@db:5432/cloudnotes`; URL-encode reserved characters in the password.
2. Start Docker Desktop and confirm `docker info` can connect to the engine.
3. From the repository root, run:

   ```powershell
   docker compose -f docker/docker-compose.yml up --build -d
   ```

   If host port 80 is unavailable, set `$env:APP_HTTP_PORT = '8080'` in PowerShell before starting Compose, then use `http://localhost:8080/` for the app.

4. Open:
   - App: `http://localhost/`
   - Backend health: `http://localhost:5000/api/health`
   - Prometheus: `http://localhost:9091/`
   - Grafana: `http://localhost:3001/` (login is `admin`; set `GF_SECURITY_ADMIN_PASSWORD` in the env file)

5. Check service state with `docker compose -f docker/docker-compose.yml ps` and logs with `docker compose -f docker/docker-compose.yml logs -f backend`.
6. Stop services with `docker compose -f docker/docker-compose.yml down`. The named `pgdata` volume persists. Use `down -v` only when you intend to erase local database contents.

Compose publishes its host ports on `127.0.0.1` so the unauthenticated demo services are local to the machine by default.

## Kubernetes / Minikube

The Kubernetes manifests use namespace `cloudnotes`. They include application Deployments and Services, a PostgreSQL PVC, an Ingress for host `cloudnotes.local`, Prometheus, and KEDA ScaledObjects.

1. Start a cluster, for example:

   ```powershell
   minikube start --driver=docker
   ```

2. Install an Nginx ingress controller and KEDA in the cluster. Confirm the KEDA Prometheus scaler can reach the `prometheus` Service in `cloudnotes`.
3. Replace the example database credentials in `kubernetes/postgres-secret.yaml` before deployment. The checked-in file contains placeholders, not production secrets.
4. Apply the manifests:

   ```powershell
   kubectl apply -f kubernetes/
   kubectl get pods,services,ingress -n cloudnotes
   ```

5. Access through the ingress controller using `cloudnotes.local` (map it to the controller address in the local hosts file if needed). To use the frontend NodePort instead, run `minikube service frontend -n cloudnotes`.
6. Inspect scaling with `kubectl get scaledobjects,hpa -n cloudnotes` and replica counts with `kubectl get deployments -n cloudnotes`.

Kubernetes monitoring deploys Prometheus and the alert rules in `kubernetes/monitoring.yaml`. The provisioned Grafana dashboard is part of the local Compose setup; the Kubernetes manifests do not deploy Grafana.

## AWS provisioning

The Terraform configuration creates a VPC and public subnet, security groups, an EC2 host for Jenkins, an EC2 host bootstrapped with K3s/KEDA/Ingress, an S3 bucket, and a billing alarm. An email subscription is created only when `billing_alarm_email` is set. The hosts are in a single public subnet and the app cluster is a single EC2 node; this is a course demonstration, not a highly available production topology.

1. Review `terraform/variables.tf`, `terraform/modules/vpc/main.tf`, and `terraform/main.tf`. The app's HTTP/HTTPS ports (80/443) are public; SSH, Jenkins (8080), Grafana (3001), and Prometheus (9091) are restricted to `admin_cidr`. The backend port (5000) is not published publicly.
2. Provide valid AWS credentials, the provisioning SSH public key, and a trusted admin CIDR (use a single-address `/32` where practical). Supply `ssh_public_key` and `admin_cidr` in a local `terraform.tfvars` (ignored by Git) or with `-var` arguments. Never put a private key in Terraform variables or source control.
3. Optionally set `billing_alarm_email`. Without it, Terraform creates the billing alarm and SNS topic without an email subscription.
4. Initialize and inspect the plan:

   ```powershell
   terraform -chdir=terraform init
   terraform -chdir=terraform plan
   ```

5. Apply only after reviewing planned resources and costs:

   ```powershell
   terraform -chdir=terraform apply
   ```

   `start_mumbai.bat` runs `start_automated_terraform.ps1`, which applies Terraform without prompting, configures Jenkins, updates a GitHub webhook, and may commit and push the Jenkinsfile. Before using it, create `.secrets/github_token.txt` and `.secrets/dockerhub_password.txt`; these files are ignored by Git. The script uses `%USERPROFILE%\.ssh\cloudnotes-aws` by default for your provisioning connection. The Jenkins EC2 host generates and keeps its own dedicated deployment key; the start script registers only its public key on the app host. The private CI key is not copied from the workstation. Load the provisioning key in the Windows SSH agent before starting the script. The GitHub webhook and Jenkinsfile commit remain in GitHub after AWS teardown.

6. Retrieve current host addresses with:

   ```powershell
   terraform -chdir=terraform output
   ```

   Public IPs are dynamic and may differ from historical documentation. Terraform bootstraps the infrastructure and cluster; CloudNotes becomes available only after the Kubernetes manifests and application images are deployed successfully. Repository files alone do not prove that a live endpoint is running.

## Jenkins delivery pipeline

The root `Jenkinsfile` defines checkout, backend image/test execution, TruffleHog secret scanning, Docker image builds, Trivy scanning, Docker Hub publication, and deployment by SSH to the K3s app host. It uses a GitHub push trigger. The startup script configures `dockerhub-credentials` and `app-server-ssh-key` from the ignored secret files and dedicated Jenkins key pair; manual Jenkins setup must create credentials with those IDs.

The Jenkins pipeline uses a configured `APP_SERVER_IP`; update it for the current app host through the project automation or Jenkins configuration before triggering a deployment. Use immutable build-number image tags to identify a release; `latest` is also pushed for convenience.

## Application endpoints and metrics

The API uses JSON. Create a note with `POST /api/notes` and body `{"title":"Example","body":"Text"}`. Search with `GET /api/notes?search=Example`. See the README for the complete endpoint table. Prometheus scrapes backend `/metrics` at a 15-second interval; KEDA queries the aggregate Flask HTTP request rate. KEDA minimum/maximum replica settings and thresholds are in `kubernetes/hpa.yaml`.

## Stop and clean up

- Local: `docker compose -f docker/docker-compose.yml down`.
- Kubernetes: `kubectl delete namespace cloudnotes` (this deletes namespaced resources and may remove the PVC/data depending on the storage class and reclaim policy).
- AWS: `terraform -chdir=terraform destroy` after reviewing the destroy plan, or run `stop_mumbai.bat`, which asks Terraform for its normal confirmation before destroying resources in the current state. Verify in the AWS console for resources outside that state, retained data, and remaining charges. GitHub webhook settings, pushed commits, and Docker Hub images are outside Terraform and persist after teardown.

Never report that cleanup costs are exactly zero without checking for retained resources, snapshots, or billing delays.

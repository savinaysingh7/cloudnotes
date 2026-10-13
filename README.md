# CloudNotes

CloudNotes is a containerized note-taking application submitted for **INT378: Advancements in Cloud and DevOps**. It combines a static Nginx frontend, a Flask REST API, PostgreSQL persistence, local Docker Compose orchestration, Kubernetes deployment manifests, Terraform for AWS infrastructure, Jenkins CI/CD, and Prometheus/Grafana observability.

The application supports creating, listing, searching, editing, and deleting notes. This is an educational demonstration, not a production-ready service: the API has no user authentication, HTTP examples use placeholders, and exposed AWS addresses can change when infrastructure is recreated. AWS provisioning uses a local key for operator access and a separate Jenkins deployment key; both private keys and all tokens/passwords belong in ignored local files only.

## Documentation

- [Project report (PDF)](CloudNotesProjectReport.pdf)
- [Editable project report source (Markdown)](CloudNotes_Project_Report.md)
- [Run and deployment guide](HOW_TO_RUN.md)
- [Viva questions and answers](VIVA.md)

## Architecture

```text
Browser -> Nginx frontend -> Flask API -> PostgreSQL
                               |  \
                               |   -> /metrics -> Prometheus -> Grafana (Compose)
                               -> note CRUD API

GitHub push -> Jenkins -> test and security scans -> Docker Hub -> SSH/kubectl -> K3s
Terraform provisions the AWS VPC, EC2 hosts, and S3 bucket.
```

The frontend and backend have separate Dockerfiles and images. Docker Compose runs PostgreSQL, the app, Prometheus, and Grafana locally. Kubernetes manifests deploy the app, PostgreSQL, and Prometheus; KEDA scales frontend and backend replicas based on the backend HTTP request-rate metric. Grafana is provisioned for the Compose environment. The AWS application host is a single K3s node, so it is not a highly available cluster.

## Quick start

1. Install Docker Desktop / Docker Engine with Compose support.
2. From the repository root, create `docker/.env` from `docker/.env.example` and replace all `CHANGE_ME` values with local-only credentials.
3. Start the stack:

   ```powershell
   docker compose -f docker/docker-compose.yml up --build -d
   ```

4. Open the app at `http://localhost/`, Grafana at `http://localhost:3001/`, and Prometheus at `http://localhost:9091/`. If Windows reserves port 80, set `$env:APP_HTTP_PORT = '8080'` before Compose and open `http://localhost:8080/`.
5. Stop the stack with `docker compose -f docker/docker-compose.yml down`. Add `-v` only when you intend to delete the local PostgreSQL volume and its data.

See [HOW_TO_RUN.md](HOW_TO_RUN.md) for Kubernetes and AWS instructions, environment variables, verification, and cleanup.

## Repository map

| Path | Purpose |
| --- | --- |
| `app/backend/` | Flask API, SQLAlchemy model, Dockerfile, and pytest suite |
| `app/frontend/` | Static UI, Nginx config, and frontend Dockerfile |
| `docker/` | Compose definitions, environment template, and recovery script |
| `kubernetes/` | Namespace, app/database deployments, storage, ingress, Prometheus, and KEDA scaling |
| `terraform/` | AWS provider configuration, modules, outputs, and billing alarm |
| `Jenkinsfile`, `jenkins/` | Pipeline and Jenkins configuration |
| `monitoring/` | Local Prometheus rules and Grafana provisioning/dashboard |
| `diagrams/` | Architecture and workflow diagrams used by the report |
| `tests/e2e/` | Puppeteer browser automation |

## API summary

| Method | Endpoint | Behavior |
| --- | --- | --- |
| `GET` | `/api/health` | Returns `{"status":"ok"}` |
| `GET` | `/api/notes` | Lists notes; accepts optional `?search=` for title/body matching |
| `POST` | `/api/notes` | Creates a note from JSON `title` and `body` |
| `PUT` | `/api/notes/<id>` | Updates supplied title/body fields |
| `DELETE` | `/api/notes/<id>` | Deletes a note |
| `GET` | `/metrics` | Exposes Prometheus metrics |

## Deployment overview

- **Compose:** intended for local development and demonstration.
- **Kubernetes / Minikube:** applies the manifests in `kubernetes/`; install an ingress controller and KEDA first when using the ingress and ScaledObjects.
- **AWS:** Terraform provisions EC2 hosts and related infrastructure; `start_mumbai.bat` orchestrates provisioning and setup. Read the run guide and inspect Terraform plan, costs, and security-group exposure before applying.

To inspect current AWS endpoints after provisioning, run `terraform -chdir=terraform output`. Do not rely on IPs copied into older reports; public EC2 addresses can change.

## Security and scope

The demo has no authentication or authorization. The Terraform security groups include public access rules for demonstration. Replace placeholder secrets, restrict SSH/Jenkins/monitoring access, use TLS, and add authentication before any internet-facing use. Terraform state, AWS credentials, SSH private keys, and populated `.env` files must not be committed.

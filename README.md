# Clubscope Platform

An Internal Developer Platform (IDP) built from scratch as a learning project and portfolio piece — designed to run any containerized service, provisioned entirely through Infrastructure as Code.

## Goal

This project demonstrates the core building blocks of a modern platform engineering stack: infrastructure provisioning, container orchestration, GitOps deployment, observability, and security — all built incrementally and documented at each stage.

## Status

🚧 Work in progress. Currently in local development phase using `kind`, with a planned migration to a managed cloud Kubernetes service (GKE, then AWS EKS).

## Architecture

- **Local development:** [`kind`](https://kind.sigs.k8s.io/) (Kubernetes in Docker)
- **Infrastructure as Code:** Terraform
- **Container orchestration:** Kubernetes
- **GitOps** (planned): ArgoCD
- **Observability** (planned): Prometheus + Grafana
- **Cloud target** (planned): GKE → AWS EKS

## Repository structure

\`\`\`
clubscope-platform/
├── modules/            # Reusable Terraform modules (networking, security, compute, database, observability)
├── environments/
│   └── development/    # Environment-specific Terraform config (currently: kind cluster)
├── kind-config.yaml     # Local kind cluster node topology
├── LICENSE
└── README.md
\`\`\`

## Getting started (local development)

### Prerequisites
- Docker
- kubectl
- kind
- Terraform >= 1.9.0

### Provision the cluster

\`\`\`bash
cd environments/development
terraform init
terraform plan
terraform apply
\`\`\`

### Verify

\`\`\`bash
kubectl get nodes
\`\`\`

## Roadmap

- [x] Local Kubernetes cluster via Terraform (kind)
- [ ] Example service with CI pipeline
- [ ] GitOps deployment with ArgoCD
- [ ] Observability stack (Prometheus/Grafana)
- [ ] Security policies (secrets management, admission control)
- [ ] Migration to GKE
- [ ] Migration to AWS EKS

## Author

Dixon Araya Arias — [GitHub](https://github.com/TavoA2)

## License

MIT — see [LICENSE](LICENSE)

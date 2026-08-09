# Clubscope Platform

An Internal Developer Platform (IDP) built from scratch as a learning project and portfolio piece — designed to run any containerized service, provisioned entirely through Infrastructure as Code, deployed via GitOps, and observed through a full Prometheus/Grafana stack.

## Goal

This project demonstrates the core building blocks of a modern platform engineering stack: infrastructure provisioning, container orchestration, CI/CD, GitOps deployment, observability, and policy-as-code security — built incrementally and documented at each stage.

## Status

🚧 Work in progress. Local development phase complete using `kind`. Next: migration to a managed cloud Kubernetes service (GKE, then AWS EKS).

## Architecture

- **Local development:** [`kind`](https://kind.sigs.k8s.io/) (Kubernetes in Docker)
- **Infrastructure as Code:** Terraform
- **Container orchestration:** Kubernetes
- **CI:** GitHub Actions → GitHub Container Registry (ghcr.io)
- **GitOps:** ArgoCD (automated sync + self-heal)
- **Observability:** Prometheus + Grafana, custom app metrics via `prometheus_client`
- **Security/Policy:** Kyverno (policy enforcement), Kubernetes Secrets
- **Cloud target (planned):** GKE → AWS EKS

## Repository structure

\`\`\`
clubscope-platform/
├── modules/                  # Reusable Terraform modules (future: networking, security, compute, database, observability)
├── environments/
│   └── development/          # Terraform config for the kind cluster
├── apps/
│   └── hello-service/        # Example Flask service, instrumented with Prometheus metrics
│       ├── app.py
│       ├── Dockerfile
│       ├── requirements.txt
│       └── k8s/               # Raw manifests (reference/dev use)
├── gitops/
│   ├── hello-service/         # ArgoCD-managed manifests (source of truth for the cluster)
│   ├── policies/              # Kyverno ClusterPolicies
│   ├── hello-service-app.yaml # ArgoCD Application
│   └── policies-app.yaml      # ArgoCD Application
├── .github/workflows/         # CI pipelines
├── kind-config.yaml
├── LICENSE
└── README.md
\`\`\`

## What's implemented

### Infrastructure (Phase 1)
Kubernetes cluster provisioned declaratively with Terraform, using the `kind` provider for local development at zero cloud cost.

### Application + CI (Phase 2)
A Flask service (`hello-service`) containerized with a multi-stage Dockerfile (non-root user, gunicorn). GitHub Actions builds and publishes immutable, SHA-tagged images to GitHub Container Registry on every push.

### GitOps (Phase 3)
ArgoCD continuously reconciles the cluster against the `gitops/` path in this repo. Automated sync and self-healing are enabled — manual `kubectl` changes that drift from Git are automatically reverted.

### Observability (Phase 4)
`kube-prometheus-stack` (Prometheus + Grafana + Alertmanager) deployed via Helm. `hello-service` exposes custom metrics (request count, latency histogram) scraped automatically through a `ServiceMonitor`.

### Security & Policy (Phase 5)
Kyverno enforces cluster-wide policies:
- All containers must declare CPU/memory `requests` and `limits`
- The `:latest` image tag is disallowed — only immutable, versioned tags are permitted

Sensitive values (e.g. Grafana admin credentials) are stored as Kubernetes Secrets rather than passed as plain Helm values.

## Getting started (local development)

### Prerequisites
- Docker
- kubectl
- kind
- Terraform >= 1.9.0
- Helm

### Provision the cluster

\`\`\`bash
cd environments/development
terraform init
terraform apply
\`\`\`

### Install ArgoCD

\`\`\`bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side
kubectl apply -f gitops/hello-service-app.yaml
kubectl apply -f gitops/policies-app.yaml
\`\`\`

### Install observability stack

\`\`\`bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
kubectl create namespace monitoring
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
\`\`\`

### Access dashboards

\`\`\`bash
kubectl port-forward svc/argocd-server -n argocd 8081:443       # ArgoCD UI
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80   # Grafana
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090  # Prometheus
\`\`\`

## Roadmap

- [x] Local Kubernetes cluster via Terraform (kind)
- [x] Example service with CI pipeline
- [x] GitOps deployment with ArgoCD
- [x] Observability stack (Prometheus/Grafana + custom app metrics)
- [x] Security policies (Kyverno, Kubernetes Secrets)
- [ ] Runbook + Architecture Decision Records
- [ ] Migration to GKE
- [ ] Migration to AWS EKS
- [ ] Second example service (demonstrate multi-service platform + service-to-service DNS)

## Author

Dixon Araya Arias — [GitHub](https://github.com/TavoA2)

## License

MIT — see [LICENSE](LICENSE)

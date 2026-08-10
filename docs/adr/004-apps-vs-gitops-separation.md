# ADR 004: Separate apps/ (application code) from gitops/ (deployed state)

## Status
Accepted

## Context
Kubernetes manifests for a service could live in a single location alongside its application code. As the platform grows to support multiple services, this creates ambiguity about which manifests represent "reference config for developers" versus "the actual desired state ArgoCD should reconcile the cluster against."

## Decision
Maintain two separate manifest locations per service:
- `apps/<service>/k8s/` — reference manifests owned conceptually by the application/developer side; useful for local `kubectl apply` testing without touching GitOps state
- `gitops/<service>/` — the manifests ArgoCD actually watches and reconciles; this is the single source of truth for what runs in the cluster

Only `gitops/` is wired to an ArgoCD `Application` resource.

## Consequences
**Positive:**
- Mirrors a common real-world split between "app team" and "platform team" ownership, even in a single-person project — good for explaining platform team boundaries in interviews
- Prevents accidental cluster drift from someone testing manifests locally under `apps/`
- `gitops/` can evolve independently (e.g. adding a `ServiceMonitor` or `PrometheusRule` that isn't part of the app's own repo concerns)

**Negative / trade-offs accepted:**
- Duplication risk: the Deployment/Service definitions exist in two places and can drift out of sync with each other if not kept intentionally aligned
- Slightly more directories to navigate for a single-service project (the benefit becomes clearer as more services are added)

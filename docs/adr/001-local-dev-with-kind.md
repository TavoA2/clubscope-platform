# ADR 001: Use kind for local development instead of provisioning EKS directly

## Status
Accepted

## Context
Building this platform requires a Kubernetes cluster to iterate against. Provisioning EKS directly from the start would allow testing against a "real" cloud environment, but EKS has a fixed control plane cost (~$0.10/hour, ~$73/month) regardless of usage, plus EC2 node costs — incurred from the moment the cluster exists, not just when actively used.

## Decision
Use `kind` (Kubernetes in Docker) for all local development and iteration. Cloud provisioning (starting with GKE, due to its free control plane tier, then AWS EKS) is deferred to a later phase, once the core platform design is validated locally.

## Consequences
**Positive:**
- Zero infrastructure cost during the (long) iterative development phase
- Fast cluster creation/teardown (~1-2 minutes vs. 10-15+ minutes for EKS)
- Safe to break things repeatedly without financial risk

**Negative / trade-offs accepted:**
- `kind` simulates nodes as Docker containers, not real VMs — some cloud-specific behaviors (real VPC networking, IAM-based node permissions, cloud load balancers) aren't exercised locally
- Terraform provider differs (`tehcyx/kind` vs `hashicorp/aws`), so the local Terraform code isn't 1:1 with what will run in production — this is mitigated by keeping modules environment-agnostic where possible

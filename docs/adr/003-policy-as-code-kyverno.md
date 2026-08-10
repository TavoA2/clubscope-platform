# ADR 003: Enforce cluster policies with Kyverno instead of documentation-only guidelines

## Status
Accepted

## Context
Best practices like "always set resource requests/limits" and "never use :latest tags" were being followed manually, relying on discipline alone. This doesn't scale to a team setting and doesn't prevent mistakes — it only documents intent.

## Decision
Adopt Kyverno as an admission controller enforcing cluster-wide policies (`ClusterPolicy` resources), rejecting non-compliant resources at creation time rather than relying on code review or documentation alone. Policies are managed as GitOps-controlled YAML under `gitops/policies/`, same lifecycle as any other cluster resource.

## Consequences
**Positive:**
- Violations are impossible to merge into the running cluster, not just discouraged
- Policies are version-controlled and auditable, same as application code
- Kyverno policies are written in native Kubernetes YAML (no new DSL to learn, unlike OPA/Rego)

**Negative / trade-offs accepted:**
- Adds a component to operate and keep healthy (Kyverno's own pods/webhooks)
- Overly strict policies can block legitimate emergency changes if not carefully scoped — mitigated by keeping initial policies minimal (resource limits, tag immutability) rather than broad

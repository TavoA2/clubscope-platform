# ADR 002: Use commit-SHA image tags instead of :latest

## Status
Accepted

## Context
Initial deployment manifests referenced container images using the `:latest` tag. In practice, when CI published a new image with the same `:latest` tag, ArgoCD detected no diff in the Git manifest (the tag string hadn't changed), so it never triggered a redeploy — running pods kept serving stale code despite a new image being available.

## Decision
CI publishes each image with an immutable tag based on the commit's short SHA (e.g. `hello-service:3bf68f0`), in addition to `latest` for convenience/debugging. GitOps-managed deployment manifests (`gitops/`) always reference the SHA tag, never `latest`. A Kyverno policy (`disallow-latest-tag`) enforces this at the cluster level, rejecting any Pod spec using `:latest`.

## Consequences
**Positive:**
- Every Git commit to a manifest produces a real, meaningful diff — GitOps reconciliation works correctly
- Deployments are traceable: a running image's tag maps directly to a specific commit and CI run
- Policy enforcement prevents the mistake from being reintroduced by anyone (including future me)

**Negative / trade-offs accepted:**
- Slightly more manual step to update the manifest with the new SHA after each app change (mitigated by this being the same workflow as any other config change — nothing extra to remember)
- `latest` still exists as a tag for local debugging convenience, so discipline is required to never reference it in `gitops/`

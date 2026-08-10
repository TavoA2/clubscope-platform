# Runbook: hello-service Down

## Alert
`HelloServiceDown` — fires when `hello-service` has 0 available replicas for more than 1 minute.

## Severity
Critical

## Symptoms
- Prometheus alert `HelloServiceDown` is `Firing`
- `kubectl get pods -l app=hello-service` shows no running pods
- Requests to the service endpoint fail or time out

## Diagnosis

1. Check current deployment status:
   \`\`\`bash
   kubectl get deployment hello-service
   kubectl get pods -l app=hello-service
   \`\`\`

2. Check recent events for the deployment/pods:
   \`\`\`bash
   kubectl describe deployment hello-service
   kubectl get events --sort-by=.lastTimestamp | grep hello-service
   \`\`\`

3. Check ArgoCD sync status — confirm whether the cluster state matches Git:
   \`\`\`bash
   kubectl get application hello-service -n argocd -o jsonpath='{.status.sync.status}'
   \`\`\`
   - If `OutOfSync`: something diverged from the desired state in Git.
   - If `Synced` but still down: the desired state itself may be wrong (e.g. replicas set to 0 in Git).

## Mitigation

**If sync is paused or manual:**
\`\`\`bash
kubectl patch application hello-service -n argocd --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true}}}}'
\`\`\`

**If replicas were manually scaled down outside of Git (drift):**
ArgoCD's `selfHeal: true` should auto-correct this within its reconciliation interval. If it doesn't within ~1 minute, force a manual sync:
\`\`\`bash
kubectl get application hello-service -n argocd
# or via UI: Applications > hello-service > Sync
\`\`\`

**If the desired state in Git itself is wrong** (e.g. someone committed `replicas: 0`):
Revert the offending commit in \`gitops/hello-service/deployment.yaml\` and push — ArgoCD will pick up the fix automatically.

## Verification

\`\`\`bash
kubectl get pods -l app=hello-service
curl http://localhost:8080/health   # via port-forward
\`\`\`

Confirm the Prometheus alert returns to \`Inactive\` at \`http://localhost:9090/alerts\`.

## Root cause (this simulation)
Manually scaled to 0 replicas as a deliberate test of the alerting pipeline, with ArgoCD auto-sync temporarily disabled to allow the drift to persist long enough for the alert to fire.

## Prevention
- Auto-sync + self-heal should remain enabled on `hello-service` at all times in normal operation
- Any intentional maintenance requiring scale-to-zero should be done via a Git commit (not a manual `kubectl` command), so the change is tracked and reversible

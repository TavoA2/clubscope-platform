# Runbook: hello-service High Latency

## Alert
`HelloServiceHighLatency` — fires when p95 request latency exceeds 500ms for more than 2 minutes.

## Severity
Warning

## Symptoms
- Prometheus alert `HelloServiceHighLatency` is `Firing`
- Slow responses reported by users/clients
- `hello_service_request_duration_seconds` histogram shows elevated values

## Diagnosis

1. Confirm the actual p95 latency via Prometheus query (Prometheus UI > Query):
   \`\`\`
   histogram_quantile(0.95, rate(hello_service_request_duration_seconds_bucket[5m]))
   \`\`\`

2. Check resource usage — is the pod CPU-throttled?
   \`\`\`bash
   kubectl top pods -l app=hello-service
   \`\`\`
   Compare against the \`resources.limits.cpu\` defined in the deployment (\`200m\`). If usage is consistently near the limit, CPU throttling is a likely cause.

3. Check replica count — is traffic being spread across enough pods?
   \`\`\`bash
   kubectl get deployment hello-service
   \`\`\`

4. Check for recent deployments/changes that might correlate with the latency increase:
   \`\`\`bash
   kubectl rollout history deployment hello-service
   \`\`\`

## Mitigation

**If CPU-throttled:**
Temporarily increase CPU limits in \`gitops/hello-service/deployment.yaml\`, commit and push (let ArgoCD roll it out) — this is a short-term fix; longer term, profile the app for inefficiencies.

**If under-provisioned for current load:**
Scale up replicas via Git:
\`\`\`bash
# edit replicas in gitops/hello-service/deployment.yaml, then:
git add gitops/hello-service/deployment.yaml
git commit -m "Scale hello-service replicas for load"
git push
\`\`\`

**If caused by a recent bad deployment:**
Roll back via Git revert of the offending commit — do not use \`kubectl rollout undo\` directly, since ArgoCD's self-heal would immediately revert your manual rollback back to what's in Git.

## Verification

Re-run the PromQL query from Diagnosis step 1 and confirm it drops below 0.5s. Confirm the alert returns to \`Inactive\`.

## Prevention
- Consider adding a Horizontal Pod Autoscaler (HPA) so replica count adjusts automatically under load, rather than requiring manual intervention
- Review resource limits periodically against actual usage patterns via Grafana dashboards

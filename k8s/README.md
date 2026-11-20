# Stage 3 – Kubernetes (Week 11)

**Owner:** _TBD (Kubernetes Engineer)_

## Requirements

- [ ] Local cluster with **minikube**
- [ ] App as a **Deployment with 2 replicas**, exposed with a **Service**
- [ ] **Self-healing:** delete a Pod, show it is replaced
- [ ] **Scaling:** 2 → 4 replicas with one command
- [ ] All YAML files kept in this folder

## Planned files

```
secret.yaml        DB credentials (template only — real values never committed)
postgres.yaml      PostgreSQL Deployment/StatefulSet + PVC + Service
app-deployment.yaml
app-service.yaml   NodePort
```

## Demo commands

```bash
kubectl get pods -o wide
kubectl delete pod <app-pod>          # self-healing
kubectl get pods -w
kubectl scale deployment pwcheck --replicas=4
```

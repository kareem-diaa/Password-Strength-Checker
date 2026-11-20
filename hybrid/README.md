# Stage 4 – Hybrid (Week 12)

**Owner:** Team Lead (coordination) + whole team

## Design

| Component | Runs on | Why |
|-----------|---------|-----|
| PostgreSQL | VM from Stage 1 | Stateful data on a dedicated, long-lived machine |
| App image | Built in Stage 2 | Same artefact reused, no new code |
| App | Deployment on the Stage 3 cluster | Replication, self-healing, scaling |

The app connects to the database using the **VM's IP address**.

> Agree this layout (or the accepted alternative: cluster inside the VM) with the TA in **Week 11**.

## Requirements

- [ ] Pods reach PostgreSQL on the VM (host-only network, `listen_addresses`, `pg_hba.conf`)
- [ ] One diagram + a few sentences explaining placement
- [ ] Data still present after all app Pods are deleted

## Connectivity test (do this early in Week 11)

```bash
kubectl run pgtest --rm -it --image=postgres:16 -- \
  psql -h <VM_IP> -U pwcheck -d pwcheck -c "SELECT 1;"
```

# Measurements (Report Table 7)

Record values **as each stage is finished**, not in Week 13. Note the command used and the machine.

**Test machine:** _CPU / RAM / OS_

| Measure | VM | Containers | Kubernetes | Hybrid |
|---------|----|-----------|-----------|--------|
| Time to start the service | | | | |
| Disk space used | | | | |
| Memory used when idle | | | | |
| Behaviour when the application is stopped | | | | |
| Effort to run four copies of the application | | | | |

## How we measure

| Measure | VM | Containers | Kubernetes |
|---------|----|-----------|-----------|
| Start time | boot → `/health` returns 200 | `docker start` → `/health` 200 | `kubectl rollout status` duration |
| Disk | VM disk file size | `docker images`, `docker system df` | image size + PVC |
| Idle memory | `free -m` in VM | `docker stats --no-stream` | `kubectl top pods` (metrics-server addon) |
| App stopped | `systemctl stop` → ? | `docker stop` → ? | `kubectl delete pod` → replaced |
| Four copies | 3 more VMs / processes + load balancer | 3 more `docker run` + ports | `kubectl scale --replicas=4` |

## Raw log

| Date | Stage | Measure | Value | Command | By |
|------|-------|---------|-------|---------|----|

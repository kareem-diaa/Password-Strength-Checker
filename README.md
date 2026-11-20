# CET322 – One Service, Four Ways

**Course:** CET 322 Introduction to Cloud Computing — ElSewedy University of Technology (SUTech), Fall 2026
**Project:** Deploy one small service under four models — Virtual Machine, Containers, Kubernetes, and Hybrid — and compare them using our own measurements.

**Track:** D – Cybersecurity
**Service:** Password Strength Checker — a page that evaluates how strong a password is **without ever storing it**. Only anonymous results are kept.

---

## Team

| # | Name | Student ID | Role |
|---|------|-----------|------|
| 1 | Kareem Diaa Helal Fouad | 240100828 | Kubernetes Engineer & Team Lead |
| 2 | Yousef Walid Mohamed Ahmed | 240100013 | Application Developer |
| 3 | Mustafa Nabil Abdelraheem Abdelrahman | 240103415 | Container Engineer |
| 4 | Anwar Mohamed Anwar Nebeshy | 240102735 | VM Engineer |
| 5 | Seif Elhussein Mohamed Shorbagy | 240103306 | Documentation Engineer |

---

## Architecture (two components)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web application | Python (Flask) | Check page, strength scoring, `/stats` dashboard |
| Data store | PostgreSQL | (1) hashes of known common passwords for lookup, (2) anonymous check results — **never the password or its hash** |

> Diagram: see [`docs/architecture.md`](docs/architecture.md)

---

## Repository structure

```
app/        Application source code + database schema
vm/         Stage 1 – VM installation steps, Nginx config
docker/     Stage 2 – Dockerfile notes, run commands, (optional) docker-compose.yml
k8s/        Stage 3 – Kubernetes YAML (Deployment, Service, Secret)
hybrid/     Stage 4 – YAML + notes for app on K8s → DB on VM
docs/       Proposal, architecture, measurements, report material, screenshots
```

---

## Progress

| Stage | Week | Checkpoint | Status |
|-------|------|-----------|--------|
| D1 Proposal | 9 | Approved by TA | ⬜ |
| Stage 1 – VM | 10 | Service opens in host browser via Nginx | ⬜ |
| Stage 2 – Containers | 10 | App + DB containers on one network, data in a volume | ⬜ |
| Stage 3 – Kubernetes | 11 | 2 replicas + Service, self-healing, scale 2→4 | ⬜ |
| Stage 4 – Hybrid | 12 | App on K8s, DB on VM, data survives pod deletion | ⬜ |
| Report, video, demo | 13–14 | Submitted / presented | ⬜ |

---

## How to run

_Each stage folder will contain its own step-by-step guide. Summary to be completed:_

- **Stage 1 (VM):** see [`vm/README.md`](vm/README.md)
- **Stage 2 (Containers):** see [`docker/README.md`](docker/README.md)
- **Stage 3 (Kubernetes):** see [`k8s/README.md`](k8s/README.md)
- **Stage 4 (Hybrid):** see [`hybrid/README.md`](hybrid/README.md)

---

## Rules we follow

- **No real passwords or keys in this repo.** Use `.env` (ignored) and copy from `.env.example`.
- **Synthetic data only.** No real personal records.
- **Everyone commits their own work** from their own GitHub account. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
- AI tool usage is logged in [`docs/ai-usage.md`](docs/ai-usage.md) and declared in the report.

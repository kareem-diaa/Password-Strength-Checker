# Contributing – Team Workflow

The repository history is part of how individual marks are assessed, so **every member commits their own work from their own account.**

## Branches

- `main` — always working. No direct pushes; changes arrive via Pull Request.
- Feature branches, named by stage and task:
  - `vm/nginx-setup`
  - `docker/dockerfile`
  - `k8s/deployment`
  - `hybrid/db-on-vm`
  - `app/login-page`
  - `docs/report-stage2`

## Daily flow

```bash
git checkout main
git pull
git checkout -b k8s/deployment      # new branch for your task
# ... work ...
git add .
git commit -m "k8s: add deployment with 2 replicas"
git push -u origin k8s/deployment
# then open a Pull Request on GitHub and ask one teammate to review
```

## Commit messages

Format: `<area>: <what changed>`

- `app: hash passwords with bcrypt`
- `vm: add nginx reverse proxy config`
- `docker: persist postgres data in named volume`
- `docs: add stage 3 screenshots`

## Pull Requests

- At least **one teammate reviews** before merging. Reviewing means reading and understanding it — this is also how everyone learns every stage.
- Link the related Issue (e.g. `Closes #4`).

## Never commit

- `.env` files, passwords, tokens, private keys
- VM disk images (`.vdi`, `.ova`, `.vmdk`)
- Large binaries or database dumps with real data

## Tasks

All tasks live in **GitHub Issues**, labelled by stage (`stage-1-vm`, `stage-2-docker`, `stage-3-k8s`, `stage-4-hybrid`, `docs`, `app`) and assigned to one owner.

# Stage 2 – Containers (Week 10)

**Owner:** Mustafa Nabil Abdelraheem (Container Engineer)

## Requirements

- [x] `Dockerfile` for the application; image builds
- [x] App and PostgreSQL run as **two containers on the same Docker network**
- [x] PostgreSQL data kept in a **volume** and survives a container restart
- [ ] Docker Compose optional

## Before you run anything

Run every command below from the root of the repository.

Copy `.env.example` to `.env` and fill it in. `.env` is ignored by Git so the password never
reaches the repo. `DB_HOST` has to be the container name, not `localhost`:

```
DB_HOST=pwcheck-db
DB_PORT=5432
DB_NAME=pwcheck
DB_USER=pwcheck
DB_PASSWORD=<your own password>
```

## Commands

Network and volume:

```bash
docker network create pwcheck-net
docker volume create pgdata
```

Database:

```bash
set -a; source .env; set +a

docker run -d \
  --name pwcheck-db \
  --network pwcheck-net \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_DB="$DB_NAME" \
  -e POSTGRES_USER="$DB_USER" \
  -e POSTGRES_PASSWORD="$DB_PASSWORD" \
  postgres:16
```

Build the image and start the app:

```bash
docker build -t pwcheck:1.0 app/

docker run -d \
  --name pwcheck-app \
  --network pwcheck-net \
  -p 8000:8000 \
  --env-file .env \
  pwcheck:1.0
```

Then open http://localhost:8000

Stop everything:

```bash
docker rm -f pwcheck-app pwcheck-db
```

The volume survives this. To delete the data too: `docker volume rm pgdata`.

## Why the database has no `-p`

Only the app needs to reach the database, and the app is on the same network. Containers on a
user-defined network find each other by name, so `DB_HOST=pwcheck-db` is enough. Leaving 5432
unpublished keeps it closed to anything outside the network. The app does get `-p` because the
browser is outside.

## Dockerfile choices

- `python:3.12-slim` instead of the full image. Smaller, and fewer files means fewer things that
  can be vulnerable.
- `requirements.txt` is copied and installed before the rest of the code. Docker caches each line
  as a layer, so changing the code does not re-run `pip install`. First build took 47.9 s, a
  rebuild with no changes took 0.12 s.
- The app runs as `appuser`, not root.
- `EXPOSE 8000` is only documentation. `-p` is what opens the port.
- gunicorn binds to `0.0.0.0`. With `127.0.0.1` nothing outside the container could reach it.
- `.dockerignore` keeps `.env`, `.git` and `__pycache__` out of the image. `.gitignore` protects
  the repo, `.dockerignore` protects the image.

## Evidence

| File in `docs/screenshots/` | What it shows |
|---|---|
| `stage2-docker-ps.png` | Both containers up. The app has `0.0.0.0:8000->8000/tcp`, the database only `5432/tcp`. |
| `stage2-app-to-db.png` | The app container connecting to the database container by name and reading a row. |
| `stage2-volume-restart.png` | A row written, then `docker restart`, same row with the same timestamp. |
| `stage2-volume-container-recreate.png` | Container deleted with `docker rm -f`, new one started on the same volume, row still there. |

The last test matters more than the restart one. A container keeps its own writable layer across a
restart, so the data would survive a restart even with no volume at all. Deleting the container
removes that layer, so finding the row afterwards can only come from the volume.

## Measurements

In `docs/measurements.md`.

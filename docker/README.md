# Stage 2 – Containers (Week 10)

**Owner:** _TBD (Container Engineer)_

## Requirements

- [ ] `Dockerfile` for the application; image builds
- [ ] App and PostgreSQL run as **two containers on the same Docker network**
- [ ] PostgreSQL data kept in a **volume** and survives a container restart
- [ ] Docker Compose optional

## Commands (fill in as you go)

```bash
docker network create pwcheck-net
docker volume create pgdata
# docker run ... postgres
# docker build -t pwcheck:1.0 ../app
# docker run ... pwcheck:1.0
```

## Evidence to capture

- `docker ps` with both containers
- Data still present after `docker restart <db-container>`

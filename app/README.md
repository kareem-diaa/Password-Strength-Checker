# Application – Password Strength Checker

**Owner:** _TBD (Application Developer)_

## Scope (keep it small — extra features carry no marks)

- `/` — form: user types a password, gets a score (Very weak → Strong) and the reasons
- Checks:
  - length (min 12 recommended)
  - character classes: lowercase, uppercase, digits, symbols
  - repeated / sequential patterns (`aaaa`, `1234`, `qwerty`)
  - **found in the common-passwords list** (database lookup)
- `/stats` — anonymous totals: number of checks, score distribution, % found in the common list, most frequently failed rule
- `/health` — returns 200 (used by Kubernetes probes and start-up time measurement)
- All configuration from environment variables (see `../.env.example`)

## Why the database is needed (two communicating components)

| Table | Contents | Contains the password? |
|-------|----------|------------------------|
| `common_passwords` | SHA-256 hashes of a public common-password list (e.g. top 10,000 from SecLists) | No — these are public passwords, not users' |
| `checks` | `id, checked_at, length, score, has_lower, has_upper, has_digit, has_symbol, in_common_list` | **No** — only the result |

## Privacy rules (this is the point of the project — be able to explain them)

1. The password is **never written** to the database, logs or disk — not plain, not hashed.
2. The common-list lookup compares a SHA-256 of the input against the table; the hash is used for the query and **then discarded**, never inserted.
3. Send the form with **POST**, never GET (GET puts the password in the URL, Nginx access logs and browser history).
4. Do not log request bodies in Flask, Gunicorn or Nginx.
5. Never store the password in a cookie or session.

## Planned files

```
app.py                    Flask application
checker.py                Scoring logic (pure functions, easy to test)
requirements.txt          flask, psycopg2-binary, gunicorn
schema.sql                Tables: common_passwords, checks
load_common.py            Loads the public list into common_passwords (hashed)
data/common-passwords.txt Public list (cite source in the report)
templates/                index.html, stats.html
```

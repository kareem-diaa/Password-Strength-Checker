# Application – Password Strength Checker

A single page where you type a password and get a strength label, a score (0–100) and suggestions. The password is checked on the server and **only exists in memory for one request**. It is never stored, logged, put in a cookie or session, or shown back on the page.

## Files

```
app.py              Flask app: GET / (form), POST / (check), GET /health
checker.py          Scoring rules: a pure function evaluate(password) -> StrengthResult
templates/index.html
test_checker.py     Unit tests (scoring + web privacy checks)
requirements.txt
```

## Run locally

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                      # http://127.0.0.1:5000
python -m unittest -v              # run the tests
```

## How scoring works (NIST SP 800-63B aligned)

The full rules are in the docstring at the top of `checker.py`. In short:

- **Length matters most.** Points come from the *effective length*, meaning the characters that really add guessing work.
- **No composition rules.** Uppercase, digits and symbols are never required, and you lose nothing for leaving them out. Mixing character types gives a small bonus of at most 15 points.
- **Patterns count for nothing.** Repeated characters (`aaa`), sequences (`abc`, `321`, `qwerty`) and repeated chunks (`abcabc`) add nothing to the effective length. A well-known password hidden inside a longer one counts as a single character.
- **Common passwords** from the built-in list are capped at 5 points. This also catches simple variations like `P@ssw0rd!`.
- Fewer than 8 characters is always **Very Weak**. Input over 128 characters is rejected with a generic message.

| Score | 0–19 | 20–39 | 40–59 | 60–79 | 80–100 |
|---|---|---|---|---|---|
| Label | Very Weak | Weak | Fair | Strong | Very Strong |

## Privacy rules (be able to explain these)

1. The form uses **POST**. A GET would put the password in the URL, the server logs and the browser history.
2. The password is never written to disk, a database, logs, cookies or the session. The template has no `value=` on the input, so the password is never shown on the page.
3. Error pages show fixed text and never the exception or the input. Debug mode is always off, because its error pages show request data.
4. Request bodies over 4 KB are refused before they are read (`MAX_CONTENT_LENGTH`).
5. `Cache-Control: no-store`, a strict CSP, `Referrer-Policy: no-referrer` and HSTS are set on every response.
6. Limit: Python can't securely wipe a string from memory. We drop our reference after scoring and keep no copies, but the memory is freed only when Python reclaims it.

## Deploy behind HTTPS

Run the app with Gunicorn on localhost and put Nginx in front to handle TLS:

```bash
gunicorn --bind 127.0.0.1:8000 --workers 2 app:app
```

Gunicorn writes no access log unless you ask for one, and it never logs request bodies.

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;          # force HTTPS
}

server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    client_max_body_size 4k;
    # The default access log records only the request line (e.g. "POST /"), not the body.
    # Never add $request_body to a log_format.

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Get a free certificate with `sudo certbot --nginx -d example.com`. For a local VM without a domain, use a self-signed certificate made with `openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout key.pem -out cert.pem`. Never commit `*.pem` or `*.key` files; `.gitignore` already excludes them.

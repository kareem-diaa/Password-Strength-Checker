"""Password Strength Checker — Flask web layer.

Privacy rules enforced here:
- The password arrives only in a POST body, lives in a local variable for the
  duration of one request, and is passed to `checker.evaluate`. It is never
  written to disk, a database, a cookie, the session, or a log line, and it is
  never rendered back into the page (the form input has no `value`).
- Error responses are generic and never include request data.
- Responses are marked `no-store` so browsers and proxies don't cache them.
"""

from flask import Flask, render_template, request

from checker import MAX_LENGTH, TOO_LONG_MESSAGE, PasswordTooLongError, evaluate

app = Flask(__name__)

# Hard cap on the request body (128 characters is at most ~1.6 KB once
# UTF-8 and URL-encoded). Larger bodies are refused before parsing.
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024

GENERIC_ERROR = "Something went wrong. Please try again."


@app.get("/")
def index():
    return render_template("index.html", max_length=MAX_LENGTH)


@app.post("/")
def check():
    password = request.form.get("password", "")
    try:
        result = evaluate(password)
    except PasswordTooLongError:
        return _error(TOO_LONG_MESSAGE, 400)
    finally:
        del password  # drop our reference; nothing else holds it
    return render_template("index.html", max_length=MAX_LENGTH, result=result)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(413)
def too_large(_err):
    return _error(TOO_LONG_MESSAGE, 413)


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def generic_error(err):
    # Never pass the exception text to the page: it could include request data.
    return _error(GENERIC_ERROR, getattr(err, "code", 500))


def _error(message, status):
    return render_template("index.html", max_length=MAX_LENGTH, error=message), status


@app.after_request
def security_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
        "base-uri 'none'; frame-ancestors 'none'"
    )
    # Ignored by browsers over plain HTTP; takes effect once served over HTTPS.
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


if __name__ == "__main__":
    # Local development only. Debug mode stays off: its error pages show request data.
    app.run(host="127.0.0.1", port=5000, debug=False)

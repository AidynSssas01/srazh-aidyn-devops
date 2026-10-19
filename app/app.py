#!/usr/bin/env python3
"""
srazh-aidyn-devops — DevOps Student Application
Author: Srazh Aidyn, group IT2-2308

The application:
  1. reads student data from config/app.conf (default values);
  2. overrides them with environment variables (STUDENT_NAME, STUDENT_SURNAME,
     STUDENT_GROUP, STUDENT_ID) if they are set — e.g. `docker run -e ...`;
  3. prints the student information banner to the console (visible in `docker logs`);
  4. starts a small HTTP server so the container keeps running:
        /        -> HTML page with student information
        /health  -> JSON health-check (used by Docker HEALTHCHECK and Jenkins)
        /info    -> JSON with student information

Run once and exit (used by tests / quick check):   python3 app.py --once
Run as a web service (default, used in Docker):    python3 app.py
Only the Python standard library is used — no extra dependencies.
"""

import json
import os
import signal
import socket
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

STUDENT_KEYS = ("STUDENT_NAME", "STUDENT_SURNAME", "STUDENT_GROUP", "STUDENT_ID", "COURSE")

DEFAULTS = {
    "APP_NAME": "srazh-aidyn-devops",
    "APP_PORT": "8085",
    "APP_ENV": "development",
    "STUDENT_NAME": "Aidyn",
    "STUDENT_SURNAME": "Srazh",
    "STUDENT_GROUP": "IT2-2308",
    "STUDENT_ID": "36210",
    "COURSE": "DevOps",
}

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_CANDIDATES = (
    os.environ.get("APP_CONFIG", ""),
    os.path.join(HERE, "config", "app.conf"),          # inside the Docker image: /app/config/app.conf
    os.path.join(HERE, "..", "config", "app.conf"),    # in the repository:        app/../config/app.conf
)


def read_conf_file(path):
    """Parse a simple KEY=VALUE file. Lines starting with # are comments."""
    values = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(environ=None):
    """Return (config, sources). Priority: environment > config file > defaults."""
    environ = os.environ if environ is None else environ
    config = dict(DEFAULTS)
    sources = {key: "default" for key in config}

    for path in CONFIG_CANDIDATES:
        if path and os.path.isfile(path):
            for key, value in read_conf_file(path).items():
                config[key] = value
                sources[key] = "config file"
            config["CONFIG_PATH"] = os.path.abspath(path)
            break

    for key in list(config):
        if environ.get(key):
            config[key] = environ[key]
            sources[key] = "environment"
    return config, sources


def build_banner(config, sources=None):
    sources = sources or {}
    line = "=" * 40

    def src(key):
        return f"   [{sources[key]}]" if key in sources else ""

    return "\n".join([
        line,
        "      DevOps Student Application",
        line,
        f"Name:       {config['STUDENT_NAME']}{src('STUDENT_NAME')}",
        f"Surname:    {config['STUDENT_SURNAME']}{src('STUDENT_SURNAME')}",
        f"Group:      {config['STUDENT_GROUP']}{src('STUDENT_GROUP')}",
        f"Student ID: {config['STUDENT_ID']}{src('STUDENT_ID')}",
        f"Course:     {config['COURSE']}",
        line,
        f"App:        {config['APP_NAME']} (env: {config['APP_ENV']})",
        f"Hostname:   {socket.gethostname()}",
        f"Git commit: {os.environ.get('GIT_COMMIT', 'local')}   Build: {os.environ.get('BUILD_NUMBER', '-')}",
        line,
        "Application is running successfully!",
        line,
    ])


def info_payload(config):
    return {
        "name": config["STUDENT_NAME"],
        "surname": config["STUDENT_SURNAME"],
        "group": config["STUDENT_GROUP"],
        "student_id": config["STUDENT_ID"],
        "course": config["COURSE"],
        "app": config["APP_NAME"],
        "hostname": socket.gethostname(),
        "git_commit": os.environ.get("GIT_COMMIT", "local"),
        "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def make_handler(config):
    class StudentHandler(BaseHTTPRequestHandler):
        server_version = "SrazhAidynDevOps/1.0"

        def _send(self, code, body, content_type):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, json.dumps({"status": "ok", "app": config["APP_NAME"]}), "application/json")
            elif self.path == "/info":
                self._send(200, json.dumps(info_payload(config), indent=2), "application/json")
            elif self.path == "/":
                info = info_payload(config)
                rows = "".join(
                    f"<tr><th>{k}</th><td>{v}</td></tr>"
                    for k, v in (("Name", info["name"]), ("Surname", info["surname"]),
                                 ("Group", info["group"]), ("Student ID", info["student_id"]),
                                 ("Course", info["course"]), ("Container", info["hostname"]),
                                 ("Git commit", info["git_commit"]))
                )
                html = (
                    "<!doctype html><html><head><meta charset='utf-8'><title>DevOps Student Application</title>"
                    "<style>body{font-family:sans-serif;background:#f4f6fb;margin:40px}"
                    "div{max-width:520px;margin:auto;background:#fff;padding:24px 32px;border-radius:12px;"
                    "box-shadow:0 2px 12px #0001}th{text-align:left;padding:6px 16px 6px 0;color:#555}"
                    "h1{font-size:22px}p{color:#1a7f37;font-weight:bold}</style></head><body><div>"
                    f"<h1>DevOps Student Application</h1><table>{rows}</table>"
                    "<p>Application is running successfully!</p></div></body></html>"
                )
                self._send(200, html, "text/html; charset=utf-8")
            else:
                self._send(404, json.dumps({"error": "not found", "path": self.path}), "application/json")

        def log_message(self, fmt, *args):
            # every request goes to stdout -> visible in `docker logs`
            print(f"INFO  {self.address_string()} {fmt % args}", flush=True)

    return StudentHandler


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    config, sources = load_config()
    print(build_banner(config, sources), flush=True)
    if "--once" in argv:
        return 0

    port = int(config["APP_PORT"])
    server = HTTPServer(("0.0.0.0", port), make_handler(config))

    def stop(signum, _frame):
        # `docker stop` sends SIGTERM: shut down gracefully instead of waiting 10 s for SIGKILL
        print(f"INFO  Signal {signum} received, application stopped", flush=True)
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    print(f"INFO  HTTP server listening on port {port} (/, /health, /info)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("INFO  Application stopped", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

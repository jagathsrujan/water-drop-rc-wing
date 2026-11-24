"""ClaudeBridge - a small Fusion add-in that runs Python sent from a local client inside the live Fusion GUI.

- Listens on 127.0.0.1:8765 only. Every request must carry the token written to token.txt next to this file
  (a new random token each time the add-in starts), so other users or web pages cannot use it.
- Code runs on Fusion's main thread (CustomEvent), so the model updates on screen while it is built.
  Long jobs call adsk.doEvents() (helper refresh() in the namespace) to repaint the viewport.
- One persistent namespace: names defined by one request stay for the next.
Client: tools/fusion_bridge/fx.py
"""
import adsk.core
import adsk.fusion
import contextlib
import io
import json
import os
import secrets
import threading
import time
import traceback
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", 8765
EVENT_ID = "ClaudeBridge_exec"
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(HERE, "token.txt")

app = adsk.core.Application.get()
ui = app.userInterface
_handlers = []
_server = None
_jobs = {}
_lock = threading.Lock()
_token = ""


def refresh():
    """Repaint the viewport during a long job."""
    adsk.doEvents()
    try:
        app.activeViewport.refresh()
    except Exception:
        pass


NS = {"adsk": adsk, "app": app, "ui": ui, "refresh": refresh, "__name__": "claude_bridge_ns"}


class _ExecHandler(adsk.core.CustomEventHandler):
    def notify(self, args):
        job_id = args.additionalInfo
        with _lock:
            job = _jobs.get(job_id)
        if job is None:
            return
        out = io.StringIO()
        t0 = time.time()
        ok = True
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                exec(compile(job["code"], job.get("name", "<claude>"), "exec"), NS)
        except Exception:
            ok = False
            out.write(traceback.format_exc())
        job["result"] = {"ok": ok, "output": out.getvalue(), "seconds": round(time.time() - t0, 2)}
        job["done"].set()


class _Http(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorised(self):
        return secrets.compare_digest(self.headers.get("X-Token", ""), _token)

    def do_GET(self):
        if not self._authorised():
            return self._send(403, {"ok": False, "output": "bad token"})
        if self.path.startswith("/ping"):
            return self._send(200, {"ok": True, "output": "pong"})
        if self.path.startswith("/result/"):
            job_id = self.path.split("/result/", 1)[1]
            job = _jobs.get(job_id)
            if job is None:
                return self._send(404, {"ok": False, "output": "no such job"})
            if not job["done"].is_set():
                return self._send(202, {"ok": True, "pending": True, "job": job_id})
            with _lock:
                _jobs.pop(job_id, None)
            return self._send(200, job["result"])
        return self._send(404, {"ok": False, "output": "unknown path"})

    def do_POST(self):
        if not self._authorised():
            return self._send(403, {"ok": False, "output": "bad token"})
        n = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(n).decode("utf-8"))
        job_id = uuid.uuid4().hex
        job = {"code": req["code"], "name": req.get("name", "<claude>"), "done": threading.Event()}
        with _lock:
            _jobs[job_id] = job
        app.fireCustomEvent(EVENT_ID, job_id)
        wait = float(req.get("wait", 300))
        if job["done"].wait(wait):
            with _lock:
                _jobs.pop(job_id, None)
            return self._send(200, job["result"])
        return self._send(202, {"ok": True, "pending": True, "job": job_id})


def run(context):
    global _server, _token
    try:
        _token = secrets.token_hex(16)
        with open(TOKEN_FILE, "w") as f:
            f.write(_token)
        ev = app.registerCustomEvent(EVENT_ID)
        h = _ExecHandler()
        ev.add(h)
        _handlers.append(h)
        _server = ThreadingHTTPServer((HOST, PORT), _Http)
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    except Exception:
        ui.messageBox("ClaudeBridge failed to start:\n" + traceback.format_exc())


def stop(context):
    global _server
    try:
        if _server is not None:
            _server.shutdown()
            _server.server_close()
            _server = None
        app.unregisterCustomEvent(EVENT_ID)
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
    except Exception:
        pass

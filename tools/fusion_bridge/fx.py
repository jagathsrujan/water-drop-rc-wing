"""Client for the ClaudeBridge Fusion add-in.
  python fx.py script.py          run a file inside Fusion
  python fx.py -c "print(1)"      run a string
  python fx.py --ping             check the bridge
Exit code 1 if the code raised. The token is read from the installed add-in folder."""
import json
import os
import sys
import time
import urllib.request
import urllib.error

ADDIN = os.path.join(os.environ.get("APPDATA", ""), "Autodesk", "Autodesk Fusion 360", "API", "AddIns", "ClaudeBridge")
URL = "http://127.0.0.1:8765"


def token():
    with open(os.path.join(ADDIN, "token.txt")) as f:
        return f.read().strip()


def call(method, path, body=None, timeout=900):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(URL + path, data=data, method=method,
                                 headers={"X-Token": token(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def run(code, name="<claude>", wait=840):
    status, res = call("POST", "/", {"code": code, "name": name, "wait": wait})
    while res.get("pending"):
        time.sleep(2)
        status, res = call("GET", "/result/" + res["job"])
    return res


def main(argv):
    if argv[1:2] == ["--ping"]:
        print(call("GET", "/ping")[1])
        return 0
    if argv[1:2] == ["-c"]:
        code, name = argv[2], "<cmd>"
    else:
        name = os.path.abspath(argv[1])
        code = open(name, encoding="utf-8").read()
        code = "__file__ = %r\n" % name + code
    res = run(code, name)
    sys.stdout.write(res.get("output", ""))
    print("\n[%s in %.1f s]" % ("ok" if res.get("ok") else "ERROR", res.get("seconds", 0)))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

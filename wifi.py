"""Talks to the Wi-Fi helper (deploy/scoreboard-wifi.py), which runs as root through one sudo rule.
On a laptop (no helper installed) everything reports available=False and the Wi-Fi screens stay hidden."""
import json
import os
import subprocess
import threading
import time

HELPER = os.environ.get("SCOREBOARD_WIFI_HELPER", "/usr/local/bin/scoreboard-wifi")
OFFLINE_AFTER = int(os.environ.get("SCOREBOARD_OFFLINE_AFTER", "60"))   # seconds without Wi-Fi before the board shows the "No Wi-Fi" screen


def available():
    return os.path.exists(HELPER)


def _call(cmd, payload=None, timeout=60):
    try:
        p = subprocess.run(["sudo", "-n", HELPER, cmd], input=json.dumps(payload) if payload else None,
                           capture_output=True, text=True, timeout=timeout)
        out = json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else {}
        if p.returncode != 0 and "error" not in out:
            out["error"] = (p.stderr.strip() or "Wi-Fi helper failed")[:200]
        return p.returncode == 0, out
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        return False, {"error": str(e)[:200]}


class Wifi:
    def __init__(self):
        self.state = {"available": available(), "connected": True, "ssid": "", "signal": None, "ip": "",
                      "offline": False}
        self.attempt = {"state": "idle"}           # idle / connecting / ok / failed
        self._down_since = None
        self._lock = threading.Lock()

    def start(self):
        if self.state["available"]:
            threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            if self.attempt.get("state") != "connecting":
                self.refresh()
            time.sleep(15)

    def refresh(self):
        ok, st = _call("status", timeout=15)
        if not ok:
            return self.state
        now = time.time()
        if st.get("connected"):
            self._down_since = None
        elif self._down_since is None:
            self._down_since = now
        with self._lock:
            self.state.update(st)
            self.state["offline"] = bool(self._down_since and now - self._down_since > OFFLINE_AFTER)
        return self.state

    def scan(self):
        if not self.state["available"]:
            return {"networks": [], "error": "Wi-Fi setup isn't installed on this device."}
        ok, out = _call("scan", timeout=45)
        return out

    def connect(self, ssid, psk):
        if not self.state["available"]:
            return False
        if self.attempt.get("state") == "connecting":
            return False
        self.attempt = {"state": "connecting", "ssid": ssid, "started": time.time()}

        def work():
            ok, out = _call("connect", {"ssid": ssid, "psk": psk}, timeout=120)
            self.attempt = ({"state": "ok", "ssid": ssid, "ip": out.get("ip", "")} if ok else
                            {"state": "failed", "ssid": ssid, "error": out.get("error", "Couldn't connect.")})
            self.refresh()
        threading.Thread(target=work, daemon=True).start()
        return True

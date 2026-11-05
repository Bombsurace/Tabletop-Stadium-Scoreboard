#!/usr/bin/env python3
"""Wi-Fi helper for the scoreboard (runs as root through one sudo rule, see deploy/scoreboard-wifi.sudoers).

    scoreboard-wifi status            -> {"connected", "ssid", "signal", "ip"}
    scoreboard-wifi scan              -> {"networks": [{"ssid", "signal", "secure"}]}
    scoreboard-wifi connect           <- {"ssid": "...", "psk": "..."} on stdin (psk "" = open network)

`connect` adds the network to wpa_supplicant.conf with the highest priority, keeps the old networks, and applies it.
If it doesn't connect within CONNECT_WAIT seconds, the old file is put back, so a typo can't strand the board.
Prints one JSON object. Exit code 0 = ok, 1 = failed (the JSON says why).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

IFACE = os.environ.get("SCOREBOARD_WIFI_IFACE", "wlan0")
CONF = os.environ.get("SCOREBOARD_WPA_CONF", "/etc/wpa_supplicant/wpa_supplicant.conf")
IW = shutil.which("iw") or "/usr/sbin/iw"
WPA_CLI = shutil.which("wpa_cli") or "/usr/sbin/wpa_cli"
CONNECT_WAIT = 35
MARK = "# added by the scoreboard"


def run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def status():
    _, out = run([IW, "dev", IFACE, "link"])
    m_ssid = re.search(r"^\s*SSID:\s*(.*)$", out, re.M)
    m_sig = re.search(r"signal:\s*(-?\d+)", out)
    _, ipout = run(["ip", "-4", "-o", "addr", "show", IFACE])
    m_ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", ipout)
    connected = bool(m_ssid) and "Not connected" not in out
    return {"connected": connected and bool(m_ip), "ssid": m_ssid.group(1).strip() if m_ssid else "",
            "signal": int(m_sig.group(1)) if m_sig else None, "ip": m_ip.group(1) if m_ip else ""}


def scan():
    out = ""
    for _ in range(3):                                   # the radio is sometimes busy for a moment
        code, out = run([IW, "dev", IFACE, "scan"], timeout=25)
        if code == 0:
            break
        time.sleep(2)
    nets = {}
    for block in re.split(r"\nBSS ", "\n" + out)[1:]:
        m = re.search(r"^\s*SSID:\s*(.*)$", block, re.M)
        if not m or not m.group(1).strip() or "\\x00" in m.group(1):
            continue                                     # hidden network
        ssid = m.group(1).strip()
        sig = re.search(r"signal:\s*(-?[\d.]+)", block)
        sig = float(sig.group(1)) if sig else -100.0
        secure = bool(re.search(r"\b(RSN|WPA):", block)) or "Privacy" in block
        if ssid not in nets or sig > nets[ssid]["signal"]:
            nets[ssid] = {"ssid": ssid, "signal": round(sig), "secure": secure}
    return {"networks": sorted(nets.values(), key=lambda n: -n["signal"])}


def _blocks(text):
    return list(re.finditer(r"network\s*=\s*\{.*?\n\s*\}", text, re.S))


def _block_ssid(block):
    m = re.search(r'^\s*ssid\s*=\s*"(.*)"\s*$', block, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^\s*ssid\s*=\s*([0-9A-Fa-f]+)\s*$", block, re.M)
    if m:
        try:
            return bytes.fromhex(m.group(1)).decode("utf-8", "replace")
        except ValueError:
            return None
    return None


def apply_conf():
    code, out = run([WPA_CLI, "-i", IFACE, "reconfigure"])
    if code != 0 or "FAIL" in out:                       # no control socket: restart the interface instead
        run(["ifdown", IFACE], timeout=30)
        run(["ifup", IFACE], timeout=60)


def connect(ssid, psk):
    if not ssid or len(ssid.encode()) > 32:
        return False, {"error": "That network name isn't valid."}
    if psk and not 8 <= len(psk) <= 63:
        return False, {"error": "Wi-Fi passwords are 8 to 63 characters."}
    try:
        old = open(CONF).read()
    except OSError:
        old = "ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\nupdate_config=1\n"
    # drop any earlier entry for this same network, then add ours with the highest priority
    keep, prios = [], [0]
    pos = 0
    for m in _blocks(old):
        keep.append(old[pos:m.start()])
        blk = m.group(0)
        if _block_ssid(blk) != ssid:
            keep.append(blk)
            p = re.search(r"^\s*priority\s*=\s*(\d+)", blk, re.M)
            prios.append(int(p.group(1)) if p else 0)
        pos = m.end()
    keep.append(old[pos:])
    text = "".join(keep)
    text = re.sub(re.escape(MARK) + r"\n(?!\s*network)", "", text)     # comment left over from a removed entry
    text = re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"
    ssid_hex = ssid.encode().hex()
    if psk:
        key = "\tpsk=" + hashlib.pbkdf2_hmac("sha1", psk.encode(), ssid.encode(), 4096, 32).hex()
    else:
        key = "\tkey_mgmt=NONE"
    text += f"\n{MARK}\nnetwork={{\n\tssid={ssid_hex}\n\tscan_ssid=1\n{key}\n\tpriority={max(prios) + 1}\n}}\n"

    backup = CONF + ".before-scoreboard"
    if os.path.exists(CONF):
        shutil.copy2(CONF, backup)
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    with open(CONF + ".tmp", "w") as f:
        f.write(text)
    os.chmod(CONF + ".tmp", 0o600)
    os.replace(CONF + ".tmp", CONF)
    apply_conf()

    t0 = time.time()
    while time.time() - t0 < CONNECT_WAIT:
        st = status()
        if st["connected"] and st["ssid"] == ssid:
            return True, st
        time.sleep(2)
    # didn't work: put the old settings back so the board isn't stranded
    if os.path.exists(backup):
        shutil.copy2(backup, CONF)
        apply_conf()
    seen = any(n["ssid"] == ssid for n in scan()["networks"])
    msg = ("Couldn't join that network. Check the password and try again." if seen
           else "That network wasn't found. Is it in range and spelled right?")
    return False, {"error": msg}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        out, ok = status(), True
    elif cmd == "scan":
        out, ok = scan(), True
    elif cmd == "connect":
        req = json.loads(sys.stdin.read() or "{}")
        ok, out = connect(str(req.get("ssid", "")), str(req.get("psk", "")))
    else:
        out, ok = {"error": "unknown command"}, False
    print(json.dumps(out))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

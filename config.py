"""Settings stored in settings.json next to this file (created on first save)."""
import copy
import json
import os
import threading

from espn import DIVISIONS, TEAM_NAMES

PATH = os.environ.get("SCOREBOARD_SETTINGS",
                      os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json"))

ANIMATION_KINDS = ["touchdown", "field_goal", "safety", "two_point", "extra_point",
                   "first_down", "turnover", "red_zone", "kickoff", "halftime", "final"]

CHOICES = {
    "live_view": ("field", "scoreboard"),            # how a live game looks
    "field_theme": ("home", "favorite", "favorite_always"),
    "field_angle": ("tv", "flat"),
    "score_bug": ("bottom", "top"),
    "other_live_mode": ("grid", "live", "mix", "off"),  # no favorite playing: live scores by division / one gamecast at a time / mixed in / ignore
    "scores_scope": ("favorites", "divisions", "all", "off"),
    "scores_layout": ("single", "grid"),
    "standings_scope": ("favorites", "divisions", "afc", "nfc", "league", "off"),
    "standings_layout": ("division", "conference", "ranked"),
    "tier": ("auto", "compact", "bar", "wide", "standard"),
    "rotate": ("auto", "0", "90", "180", "270"),
}
BOOLS = ("rotate_live_favorites", "alert_all_favorites", "show_last_play", "include_last_week")
NUMBERS = (("rotate_seconds", 3, 300), ("delay_seconds", 0, 300), ("poll_live_seconds", 5, 120))

DEFAULTS = {
    "favorites": [],                    # ordered by priority, e.g. ["SEA", "KC"]
    "hidden_teams": [],                 # never rotated in (unless playing a favorite)
    "selected_divisions": [],           # used when a scope is "divisions"
    "live_view": "field",
    "field_theme": "home",
    "field_angle": "tv",
    "score_bug": "bottom",
    "rotate_seconds": 12,
    "rotate_live_favorites": True,
    "other_live_mode": "grid",
    "scores_scope": "favorites",
    "scores_layout": "single",
    "include_last_week": True,
    "standings_scope": "favorites",
    "standings_layout": "division",
    "alert_all_favorites": True,
    "delay_seconds": 0,
    "poll_live_seconds": 10,
    "tier": "auto",
    "rotate": "auto",
    "show_last_play": True,
    "viewport": {"x": 0, "y": 0, "width": 0, "height": 0},  # 0 = use the whole screen
    "animations": {k: True for k in ANIMATION_KINDS},
}

_lock = threading.Lock()
_cache = None


def _migrate(s):
    """Carry settings over from version 1."""
    if "show_other_live_games" in s and "other_live_mode" not in s:
        s["other_live_mode"] = "live" if s["show_other_live_games"] else "off"
    if s.get("show_all_scores_when_idle") and "scores_scope" not in s:
        s["scores_scope"] = "all"
    if s.get("show_standings") is False and "standings_scope" not in s:
        s["standings_scope"] = "off"
    return s


def _clean(s):
    out = copy.deepcopy(DEFAULTS)
    if not isinstance(s, dict):
        return out
    s = _migrate(dict(s))
    for key in ("favorites", "hidden_teams"):
        out[key] = list(dict.fromkeys(t for t in s.get(key, []) if t in TEAM_NAMES))
    out["selected_divisions"] = [d for d in DIVISIONS if d in (s.get("selected_divisions") or [])]
    for k in BOOLS:
        if k in s:
            out[k] = bool(s[k])
    for k, lo, hi in NUMBERS:
        try:
            out[k] = max(lo, min(hi, int(s.get(k, out[k]))))
        except (TypeError, ValueError):
            pass
    for k, allowed in CHOICES.items():
        if str(s.get(k)) in allowed:
            out[k] = str(s[k])
    vp = s.get("viewport") or {}
    for k in ("x", "y", "width", "height"):
        try:
            out["viewport"][k] = max(0, int(vp.get(k, 0)))
        except (TypeError, ValueError):
            pass
    an = s.get("animations") or {}
    for k in ANIMATION_KINDS:
        if k in an:
            out["animations"][k] = bool(an[k])
    return out


def get():
    global _cache
    with _lock:
        if _cache is None:
            try:
                with open(PATH) as f:
                    _cache = _clean(json.load(f))
            except (OSError, ValueError):
                _cache = copy.deepcopy(DEFAULTS)
        return copy.deepcopy(_cache)


def update(patch):
    global _cache
    cur = get()
    for k, v in (patch or {}).items():
        if isinstance(v, dict) and isinstance(cur.get(k), dict):
            cur[k].update(v)
        else:
            cur[k] = v
    new = _clean(cur)
    with _lock:
        _cache = new
        tmp = PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(new, f, indent=2)
        os.replace(tmp, PATH)
    return copy.deepcopy(new)

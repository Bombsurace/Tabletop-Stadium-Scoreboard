"""Turn two snapshots of the scoreboard into 'moments' worth animating.

Compares the previous poll to the current one for each game and emits
events like touchdown, field goal, first down, turnover, red zone, final.
"""

LABELS = {
    "touchdown": "TOUCHDOWN", "field_goal": "FIELD GOAL", "safety": "SAFETY",
    "two_point": "2-PT GOOD", "extra_point": "EXTRA POINT", "score": "SCORE",
    "first_down": "FIRST DOWN", "turnover": "TURNOVER", "red_zone": "RED ZONE",
    "kickoff": "KICKOFF", "halftime": "HALFTIME", "final": "FINAL",
}
# Big moments: these can interrupt even when a different game is on screen
BIG = {"touchdown", "field_goal", "safety", "two_point", "turnover"}


def make_event(kind, g, side, points=None, label=None):
    t = g[side] if side in ("home", "away") else None
    a, h = g["away"], g["home"]
    return {
        "kind": kind, "label": label or LABELS.get(kind, kind.upper()),
        "game_id": g["id"], "side": side,
        "abbr": t["abbr"] if t else None, "name": t["name"] if t else None,
        "color": t["color"] if t else "#1b2330", "alt": t["alt"] if t else "#ffd21f",
        "logo": t["logo"] if t else None, "points": points,
        "detail": g.get("last_play", ""),
        "score": f"{a['abbr']} {a['score']}  ·  {h['abbr']} {h['score']}",
        "teams": [a["abbr"], h["abbr"]],
    }


def _drive_events(p, g):
    out = []
    po, go = p.get("possession"), g.get("possession")
    lp = (g.get("last_play") or "").lower()
    if po and go and po != go:
        if "intercept" in lp:
            out.append(make_event("turnover", g, go, label="INTERCEPTION"))
        elif "fumble" in lp:
            out.append(make_event("turnover", g, go, label="FUMBLE"))
        elif "downs" in lp:
            out.append(make_event("turnover", g, go, label="TURNOVER ON DOWNS"))
        return out  # punts / kickoffs change possession quietly
    if not go or go != po:
        return out
    gd, pd = g.get("down"), p.get("down")
    gy, py = g.get("ytg"), p.get("ytg")
    first = False
    if gd == 1 and pd and pd > 1:
        first = True
    elif (gd == 1 and pd == 1 and gy is not None and py is not None
          and p.get("distance") and (py - gy) >= p["distance"]):
        first = True
    if first:
        out.append(make_event("first_down", g, go))
    if g.get("red_zone") and not p.get("red_zone"):
        out.append(make_event("red_zone", g, go))
    return out


def detect(prev, cur):
    """prev/cur: {game_id: game}. Returns a list of events."""
    out = []
    for gid, g in cur.items():
        p = prev.get(gid)
        if p is None:
            continue
        scored = False
        lp = (g.get("last_play") or "").lower()
        for side in ("away", "home"):
            d = g[side]["score"] - p[side]["score"]
            if d <= 0:
                continue
            scored = True
            if d >= 6:
                kind = "touchdown"
            elif d == 3:
                kind = "field_goal"
            elif d == 2:
                kind = "safety" if "safety" in lp else "two_point"
            elif d == 1:
                kind = "extra_point"
            else:
                kind = "score"
            out.append(make_event(kind, g, side, points=d))
        if p["state"] == "pre" and g["state"] == "in":
            out.append(make_event("kickoff", g, None))
        if g["state"] == "in" and p["state"] == "in" and not scored:
            out.extend(_drive_events(p, g))
        if g.get("status_name") == "STATUS_HALFTIME" and p.get("status_name") != "STATUS_HALFTIME":
            out.append(make_event("halftime", g, None))
        if p["state"] == "in" and g["state"] == "post":
            hs, as_ = g["home"]["score"], g["away"]["score"]
            winner = "home" if hs > as_ else "away" if as_ > hs else None
            out.append(make_event("final", g, winner))
    return out

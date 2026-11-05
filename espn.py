"""Fetch and normalize NFL data from ESPN's public (unofficial) site API.

Every game is turned into one flat dict that the display understands, so the
rest of the app never touches ESPN's raw JSON. If ESPN changes something, this
is the only file that should need fixing.
"""
import re
from datetime import datetime, timezone

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
UA = {"User-Agent": "Mozilla/5.0 (DIY desktop scoreboard)"}

DIVISIONS = {
    "AFC East": ["BUF", "MIA", "NE", "NYJ"],
    "AFC North": ["BAL", "CIN", "CLE", "PIT"],
    "AFC South": ["HOU", "IND", "JAX", "TEN"],
    "AFC West": ["DEN", "KC", "LV", "LAC"],
    "NFC East": ["DAL", "NYG", "PHI", "WSH"],
    "NFC North": ["CHI", "DET", "GB", "MIN"],
    "NFC South": ["ATL", "CAR", "NO", "TB"],
    "NFC West": ["ARI", "LAR", "SF", "SEA"],
}
TEAM_NAMES = {
    "ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills",
    "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals", "CLE": "Browns",
    "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers",
    "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars", "KC": "Chiefs",
    "LV": "Raiders", "LAC": "Chargers", "LAR": "Rams", "MIA": "Dolphins",
    "MIN": "Vikings", "NE": "Patriots", "NO": "Saints", "NYG": "Giants",
    "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SF": "49ers",
    "SEA": "Seahawks", "TB": "Buccaneers", "TEN": "Titans", "WSH": "Commanders",
}
TEAM_CITY = {
    "ARI": "Arizona", "ATL": "Atlanta", "BAL": "Baltimore", "BUF": "Buffalo",
    "CAR": "Carolina", "CHI": "Chicago", "CIN": "Cincinnati", "CLE": "Cleveland",
    "DAL": "Dallas", "DEN": "Denver", "DET": "Detroit", "GB": "Green Bay",
    "HOU": "Houston", "IND": "Indianapolis", "JAX": "Jacksonville", "KC": "Kansas City",
    "LV": "Las Vegas", "LAC": "Los Angeles", "LAR": "Los Angeles", "MIA": "Miami",
    "MIN": "Minnesota", "NE": "New England", "NO": "New Orleans", "NYG": "New York",
    "NYJ": "New York", "PHI": "Philadelphia", "PIT": "Pittsburgh", "SF": "San Francisco",
    "SEA": "Seattle", "TB": "Tampa Bay", "TEN": "Tennessee", "WSH": "Washington",
}
# Fallback colors (primary, accent) when ESPN's aren't available
TEAM_COLORS = {
    "ARI": ("#97233f", "#ffb612"), "ATL": ("#a71930", "#000000"), "BAL": ("#241773", "#9e7c0c"),
    "BUF": ("#00338d", "#c60c30"), "CAR": ("#0085ca", "#101820"), "CHI": ("#0b162a", "#c83803"),
    "CIN": ("#fb4f14", "#000000"), "CLE": ("#311d00", "#ff3c00"), "DAL": ("#003594", "#869397"),
    "DEN": ("#fb4f14", "#002244"), "DET": ("#0076b6", "#b0b7bc"), "GB": ("#203731", "#ffb612"),
    "HOU": ("#03202f", "#a71930"), "IND": ("#002c5f", "#a2aaad"), "JAX": ("#006778", "#d7a22a"),
    "KC": ("#e31837", "#ffb81c"), "LV": ("#000000", "#a5acaf"), "LAC": ("#0080c6", "#ffc20e"),
    "LAR": ("#003594", "#ffa300"), "MIA": ("#008e97", "#fc4c02"), "MIN": ("#4f2683", "#ffc62f"),
    "NE": ("#002244", "#c60c30"), "NO": ("#101820", "#d3bc8d"), "NYG": ("#0b2265", "#a71930"),
    "NYJ": ("#125740", "#ffffff"), "PHI": ("#004c54", "#a5acaf"), "PIT": ("#101820", "#ffb612"),
    "SF": ("#aa0000", "#b3995d"), "SEA": ("#002244", "#69be28"), "TB": ("#d50a0a", "#34302b"),
    "TEN": ("#0c2340", "#4b92db"), "WSH": ("#5a1414", "#ffb612"),
}
TEAM_DIVISION = {abbr: div for div, teams in DIVISIONS.items() for abbr in teams}
ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}


REMOTE_LOGO = "https://a.espncdn.com/i/teamlogos/nfl/500/{}.png"


def logo_url(abbr):
    """Logos are served (and cached on disk) by our own server: see /logo/<abbr>.png in server.py."""
    return f"/logo/{abbr}.png"


def conference_of(abbr_or_div):
    div = TEAM_DIVISION.get(abbr_or_div, abbr_or_div)
    return div.split()[0] if div else None


def static_team(abbr):
    """Team info for any team, even one not playing right now."""
    color, alt = TEAM_COLORS.get(abbr, ("#333333", "#999999"))
    name = TEAM_NAMES.get(abbr, abbr)
    city = TEAM_CITY.get(abbr, "")
    return {"abbr": abbr, "name": name, "full": f"{city} {name}".strip(), "city": city,
            "color": color, "alt": alt, "logo": logo_url(abbr)}


def _int(v, default=None):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _color(c, fallback):
    c = (c or "").strip().lstrip("#")
    return "#" + c.lower() if re.fullmatch(r"[0-9a-fA-F]{6}", c) else fallback


def parse_ts(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass
    return None


def yards_to_goal(spot, offense_abbr):
    """'BUF 34' with KC on offense -> 34 yards to go. 'KC 25' -> 75. '50' -> 50."""
    if not spot:
        return None
    m = re.match(r"^\s*([A-Z]{2,3})?\s*(\d{1,2})\s*$", str(spot).strip())
    if not m:
        return None
    side, yl = m.group(1), int(m.group(2))
    if side is None or yl == 50:
        return 50
    if not offense_abbr:
        return None
    return 100 - yl if side == offense_abbr else yl


def finish_game(g):
    """Add display helpers (period label, field position) to a base game dict.

    Field position is drawn left-to-right: x=0 is the AWAY team's goal line,
    x=100 is the HOME team's goal line. The away team always attacks right.
    """
    p = g.get("period") or 0
    g["period_label"] = ("Q%d" % p if 1 <= p <= 4 else "OT" if p == 5
                         else "%dOT" % (p - 4) if p > 5 else "")
    side = g.get("possession")
    off = g[side]["abbr"] if side in ("home", "away") else None
    ytg = yards_to_goal(g.get("spot"), off)
    g["ytg"] = ytg
    bx = fx = None
    if ytg is not None and side:
        bx = 100 - ytg if side == "away" else ytg
        d = g.get("distance")
        if d and g.get("down"):
            fx = bx + d if side == "away" else bx - d
            fx = max(0, min(100, fx))
    g["ball_x"], g["first_down_x"] = bx, fx
    if not g.get("down_text") and g.get("down") and g.get("distance") is not None:
        goal = ytg is not None and ytg <= g["distance"]
        g["down_text"] = "%s & %s" % (ORDINAL.get(g["down"], g["down"]),
                                      "Goal" if goal else g["distance"])
    return g


def _team(comp):
    t = comp.get("team") or {}
    abbr = t.get("abbreviation") or "?"
    record = ""
    for r in comp.get("records") or []:
        if r.get("type") == "total" or r.get("name") in ("overall", "All Splits"):
            record = r.get("summary", "")
            break
    if not record and comp.get("records"):
        record = comp["records"][0].get("summary", "")
    logo = logo_url(abbr)
    return {
        "id": str(t.get("id", "")), "abbr": abbr,
        "name": t.get("shortDisplayName") or t.get("name") or TEAM_NAMES.get(abbr, abbr),
        "full": t.get("displayName") or abbr,
        "city": t.get("location") or TEAM_CITY.get(abbr, ""),
        "color": _color(t.get("color"), TEAM_COLORS.get(abbr, ("#333333", "#999999"))[0]),
        "alt": _color(t.get("alternateColor"), TEAM_COLORS.get(abbr, ("#333333", "#999999"))[1]),
        "logo": logo, "score": _int(comp.get("score"), 0) or 0,
        "record": record, "timeouts": None, "winner": bool(comp.get("winner")),
    }


def parse_event(ev):
    comp = (ev.get("competitions") or [{}])[0]
    status = comp.get("status") or ev.get("status") or {}
    st = status.get("type") or {}
    teams = {c.get("homeAway"): _team(c) for c in comp.get("competitors") or []}
    home, away = teams.get("home"), teams.get("away")
    if not home or not away:
        return None
    names = []
    for b in comp.get("broadcasts") or []:
        names += b.get("names") or []
    broadcast = comp.get("broadcast") or " / ".join(dict.fromkeys(names))

    sit = comp.get("situation") or {}
    poss_id = str(sit.get("possession") or "")
    possession = "home" if poss_id and poss_id == home["id"] else \
                 "away" if poss_id and poss_id == away["id"] else None
    if sit:
        home["timeouts"] = _int(sit.get("homeTimeouts"))
        away["timeouts"] = _int(sit.get("awayTimeouts"))
    last = sit.get("lastPlay") or {}
    down = _int(sit.get("down"))
    g = {
        "id": str(ev.get("id")),
        "state": st.get("state", "pre"),
        "status_name": st.get("name", ""),
        "detail": st.get("shortDetail") or st.get("detail", ""),
        "period": _int(status.get("period"), 0),
        "clock": status.get("displayClock", ""),
        "start_ts": parse_ts(ev.get("date")),
        "home": home, "away": away, "broadcast": broadcast,
        "possession": possession,
        "down": down if down and down > 0 else None,
        "distance": _int(sit.get("distance")),
        "down_text": sit.get("shortDownDistanceText") or "",
        "spot": sit.get("possessionText") or "",
        "red_zone": bool(sit.get("isRedZone")),
        "last_play": last.get("text", "") or "",
    }
    return finish_game(g)


def parse_meta(data):
    """Which week/season this scoreboard covers."""
    season = data.get("season") or {}
    week = data.get("week") or {}
    stype = _int(season.get("type"), 2)
    num = _int(week.get("number"))
    label = ("WEEK %d" % num if stype == 2 and num else
             "PRESEASON" if stype == 1 else
             {1: "WILD CARD", 2: "DIVISIONAL", 3: "CONF. CHAMPIONSHIP", 4: "PRO BOWL",
              5: "SUPER BOWL"}.get(num, "PLAYOFFS") if stype == 3 else "")
    return {"year": _int(season.get("year")), "type": stype, "week": num, "label": label}


def parse_scoreboard(data):
    games = [g for g in (parse_event(e) for e in data.get("events") or []) if g]
    games.sort(key=lambda g: g.get("start_ts") or 0)
    return games


def fetch_scoreboard(session, params=None):
    """Returns (games, meta)."""
    r = session.get(SCOREBOARD_URL, headers=UA, timeout=10, params=params)
    r.raise_for_status()
    data = r.json()
    meta = parse_meta(data)
    games = parse_scoreboard(data)
    for g in games:
        g["week_label"] = meta["label"]
    return games, meta


def previous_week_params(meta):
    """ESPN query for the week before `meta`, or None (e.g. week 1)."""
    if not meta or not meta.get("year") or not meta.get("week"):
        return None
    t, w = meta["type"], meta["week"]
    if t == 2 and w > 1:
        return {"dates": meta["year"], "seasontype": 2, "week": w - 1}
    if t == 3 and w == 1:
        return {"dates": meta["year"], "seasontype": 2, "week": 18}
    if t == 3 and w > 1:
        return {"dates": meta["year"], "seasontype": 3, "week": 3 if w == 5 else w - 1}
    return None


def fetch_previous_week(session, meta):
    params = previous_week_params(meta)
    if not params:
        return []
    games, _ = fetch_scoreboard(session, params)
    return [g for g in games if g["state"] == "post"]


# ---------- standings ----------

def _walk_entries(node, out):
    if isinstance(node, dict):
        st = node.get("standings")
        if isinstance(st, dict):
            out.extend(st.get("entries") or [])
        for v in node.values():
            if isinstance(v, (dict, list)):
                _walk_entries(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk_entries(v, out)


def build_divisions(teams):
    out = {}
    for div, abbrs in DIVISIONS.items():
        rows = []
        for a in abbrs:
            rows.append(teams.get(a) or {"abbr": a, "name": TEAM_NAMES[a], "logo": logo_url(a),
                                         "w": 0, "l": 0, "t": 0, "pct": 0.0, "seed": 0,
                                         "color": TEAM_COLORS[a][0]})
        rows.sort(key=lambda r: (-r["pct"], -r["w"], r["l"]))
        out[div] = rows
    return out


def parse_standings(data):
    entries = []
    _walk_entries(data, entries)
    teams = {}
    for e in entries:
        t = e.get("team") or {}
        abbr = t.get("abbreviation")
        if not abbr or abbr in teams:
            continue
        stats = {}
        for s in e.get("stats") or []:
            stats[s.get("name") or s.get("type")] = s.get("value")
        w, l, ti = (_int(stats.get(k), 0) or 0 for k in ("wins", "losses", "ties"))
        try:
            pct = float(stats.get("winPercent"))
        except (TypeError, ValueError):
            gp = w + l + ti
            pct = (w + 0.5 * ti) / gp if gp else 0.0
        teams[abbr] = {
            "abbr": abbr,
            "name": t.get("shortDisplayName") or t.get("name") or TEAM_NAMES.get(abbr, abbr),
            "logo": logo_url(abbr),
            "w": w, "l": l, "t": ti, "pct": pct,
            "seed": _int(stats.get("playoffSeed"), 0) or 0,
            "color": _color(t.get("color"), TEAM_COLORS.get(abbr, ("#333333",))[0]),
        }
    return build_divisions(teams)


def ranked(divisions, conference=None):
    """All teams (or one conference) in standings order. Uses ESPN playoff seeds when available."""
    rows = [r for d, rs in divisions.items() if conference in (None, d.split()[0]) for r in rs]
    if conference and rows and all(r.get("seed") for r in rows):
        return sorted(rows, key=lambda r: r["seed"])
    return sorted(rows, key=lambda r: (-r["pct"], -r["w"], r["l"], r["abbr"]))


def fetch_standings(session):
    r = session.get(STANDINGS_URL, headers=UA, timeout=15)
    r.raise_for_status()
    return parse_standings(r.json())

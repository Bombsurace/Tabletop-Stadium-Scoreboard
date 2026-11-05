"""Fake data so you can watch the scoreboard (and every animation) without a live game.

Run:  python server.py --demo
A scripted KC @ BUF game loops every ~2 minutes, alongside a final and an upcoming game.
"""
import time

from espn import TEAM_NAMES, build_divisions, finish_game, logo_url, static_team

INFO = {  # abbr: (id, full name, color, alt color, record)
    "KC": ("12", "Kansas City Chiefs", "#e31837", "#ffb612", "5-1"),
    "BUF": ("2", "Buffalo Bills", "#00338d", "#d50a0a", "4-2"),
    "DAL": ("6", "Dallas Cowboys", "#002a5c", "#b0b7bc", "3-3"),
    "PHI": ("21", "Philadelphia Eagles", "#06424d", "#a5acaf", "4-2"),
    "SF": ("25", "San Francisco 49ers", "#aa0000", "#b3995d", "4-2"),
    "SEA": ("26", "Seattle Seahawks", "#002244", "#69be28", "4-2"),
}

# (quarter, clock, possession, down, distance, ball on, away pts, home pts, last play, special)
SCRIPT = [
    (2, "9:12", "away", 1, 10, "KC 25", 10, 7, "Kickoff, touchback.", None),
    (2, "8:40", "away", 2, 4, "KC 31", 10, 7, "Run up the middle for 6 yards.", None),
    (2, "8:01", "away", 1, 10, "KC 45", 10, 7, "Pass complete to #87 for 14 yards.", None),
    (2, "7:20", "away", 2, 3, "BUF 48", 10, 7, "Run to the left for 7 yards.", None),
    (2, "6:44", "away", 1, 10, "BUF 30", 10, 7, "Pass complete to #10 for 18 yards.", None),
    (2, "6:02", "away", 1, 10, "BUF 18", 10, 7, "Pass complete to #87 for 12 yards.", None),
    (2, "5:20", "away", 2, 4, "BUF 12", 10, 7, "Run to the right for 6 yards.", None),
    (2, "4:41", "away", None, None, "BUF 15", 16, 7, "Pass complete to #87 for 12 yards, TOUCHDOWN.", None),
    (2, "4:41", "away", None, None, "BUF 15", 17, 7, "Extra point is GOOD.", None),
    (2, "4:41", "home", 1, 10, "BUF 25", 17, 7, "Kickoff, touchback.", None),
    (2, "4:03", "home", 2, 10, "BUF 25", 17, 7, "Pass incomplete.", None),
    (2, "3:55", "away", 1, 10, "BUF 38", 17, 7, "Pass INTERCEPTED by #22, returned 13 yards.", None),
    (2, "3:12", "away", 2, 8, "BUF 36", 17, 7, "Run for 2 yards.", None),
    (2, "2:31", "away", 3, 8, "BUF 36", 17, 7, "Pass incomplete.", None),
    (2, "2:26", "away", 4, 8, "BUF 36", 17, 7, "Timeout BUF.", None),
    (2, "2:20", "away", None, None, "BUF 36", 20, 7, "54 yard field goal is GOOD.", None),
    (2, "0:00", None, None, None, None, 20, 7, "End of half.", "half"),
    (3, "15:00", "home", 1, 10, "BUF 25", 20, 7, "Kickoff, touchback.", None),
    (3, "13:48", "home", 1, 10, "BUF 41", 20, 7, "Run for 16 yards.", None),
    (3, "12:30", "home", 1, 10, "KC 33", 20, 7, "Pass complete to #14 for 26 yards.", None),
    (3, "11:52", "home", 1, 10, "KC 19", 20, 7, "Pass complete to #14 for 14 yards.", None),
    (3, "11:10", "home", 2, 3, "KC 12", 20, 7, "Run for 7 yards.", None),
    (3, "10:31", "home", None, None, "KC 15", 20, 13, "Run for 12 yards, TOUCHDOWN.", None),
    (3, "10:31", "home", None, None, "KC 15", 20, 14, "Extra point is GOOD.", None),
    (4, "0:00", None, None, None, None, 20, 14, "End of game.", "final"),
    (4, "0:00", None, None, None, None, 20, 14, "End of game.", "final"),
    (4, "0:00", None, None, None, None, 20, 14, "End of game.", "final"),
]
QUARTER = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}


def team(abbr, score, timeouts=None):
    st = static_team(abbr)
    tid, full, color, alt, rec = INFO.get(abbr, (abbr, st["full"], st["color"], st["alt"], "3-3"))
    return {"id": tid, "abbr": abbr, "name": TEAM_NAMES[abbr], "full": full, "city": st["city"],
            "color": color, "alt": alt, "logo": logo_url(abbr), "score": score, "record": rec,
            "timeouts": timeouts, "winner": False}


META = {"year": 2026, "type": 2, "week": 7, "label": "WEEK 7"}


def final_game(gid, away, ap, home, hp, ts, label, detail="Final"):
    g = finish_game({
        "id": gid, "state": "post", "status_name": "STATUS_FINAL", "detail": detail,
        "period": 4, "clock": "0:00", "start_ts": ts, "broadcast": "",
        "away": team(away, ap), "home": team(home, hp), "possession": None, "down": None,
        "distance": None, "down_text": "", "spot": "", "red_zone": False, "last_play": "",
    })
    g["away" if ap > hp else "home"]["winner"] = True
    g["week_label"] = label
    return g


def last_week():
    t = time.time() - 7 * 86400
    rows = [("KC", 27, "LV", 13), ("SEA", 31, "ARI", 24), ("BUF", 17, "MIA", 20), ("JAX", 23, "HOU", 20),
            ("PHI", 34, "NYG", 10), ("SF", 20, "LAR", 23), ("DAL", 28, "WSH", 31), ("DET", 38, "GB", 35)]
    return [final_game(f"lw{i}", a, ap, h, hp, t + i * 600, "WEEK 6",
                       "Final/OT" if i == 7 else "Final") for i, (a, ap, h, hp) in enumerate(rows)]


class Demo:
    def __init__(self, step=5.0, start=0):
        self.step = step  # seconds per play; 0 = frozen
        self.start = start  # which play to start on
        self.t0 = time.time()
        self.kick = (int(self.t0) // 300) * 300 + 3 * 3600

    def games(self, now):
        i = (self.start + (int((now - self.t0) // self.step) if self.step > 0 else 0)) % len(SCRIPT)
        q, clock, poss, down, dist, spot, ap, hp, play, special = SCRIPT[i]
        home_to = 2 if i >= 14 else 3
        g = {
            "id": "demo1", "state": "in", "status_name": "STATUS_IN_PROGRESS",
            "detail": f"{clock} - {QUARTER[q]}", "period": q, "clock": clock,
            "start_ts": self.t0 - 5400, "broadcast": "CBS",
            "away": team("KC", ap, 3), "home": team("BUF", hp, home_to),
            "possession": poss, "down": down, "distance": dist, "down_text": "",
            "spot": spot or "", "red_zone": False, "last_play": play,
        }
        if special == "half":
            g.update(status_name="STATUS_HALFTIME", detail="Halftime")
        if special == "final":
            g.update(state="post", status_name="STATUS_FINAL", detail="Final")
            g["away"]["winner"] = True
        finish_game(g)
        g["red_zone"] = bool(g["down"] and g["ytg"] is not None and g["ytg"] <= 20)

        finals = [final_game("demo2", "DAL", 24, "PHI", 27, self.t0 - 4 * 3600, "WEEK 7"),
                  final_game("demo4", "JAX", 30, "TEN", 17, self.t0 - 4 * 3600, "WEEK 7"),
                  final_game("demo5", "DET", 21, "MIN", 24, self.t0 - 4 * 3600, "WEEK 7"),
                  final_game("demo6", "LAC", 16, "DEN", 13, self.t0 - 4 * 3600, "WEEK 7")]
        g["week_label"] = "WEEK 7"
        upcoming = finish_game({
            "id": "demo3", "state": "pre", "status_name": "STATUS_SCHEDULED", "detail": "",
            "period": 0, "clock": "0:00", "start_ts": self.kick, "broadcast": "NBC",
            "away": team("SF", 0), "home": team("SEA", 0), "possession": None, "down": None,
            "distance": None, "down_text": "", "spot": "", "red_zone": False, "last_play": "",
        })
        upcoming["week_label"] = "WEEK 7"
        return [g] + finals + [upcoming]


def standings():
    teams = {}
    for abbr, name in TEAM_NAMES.items():
        if abbr in INFO:
            w, l = (int(x) for x in INFO[abbr][4].split("-"))
        else:
            w = sum(map(ord, abbr)) % 6
            l = 6 - w
        teams[abbr] = {"abbr": abbr, "name": name, "logo": logo_url(abbr), "w": w, "l": l,
                       "t": 0, "pct": w / 6, "seed": 0, "color": static_team(abbr)["color"]}
    return build_divisions(teams)

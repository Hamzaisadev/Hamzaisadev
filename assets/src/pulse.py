"""Daily 'Pulse' panel: contribution heatmap + five odometer stats, drawn from the GitHub GraphQL API.

Usage:  GITHUB_TOKEN=... python3 pulse.py <outdir> [login]
        python3 pulse.py <outdir> --demo        # fake data, for design work
"""
import datetime as dt, json, os, random, sys, urllib.parse, urllib.request
from gen import THEMES, EASE, REDUCED, svg, star
from typeset import text as T, glyphs, measure

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
LOGIN = next((a for a in sys.argv[2:] if not a.startswith("--")), "Hamzaisadev")
DEMO = "--demo" in sys.argv

RAMP = {"light": ["#E6DFD2", "#F6C7B4", "#FC9A78", "#FF6A3D", "#FF4A1C"],
        "dark": ["#1E1D1B", "#4A2418", "#8A3519", "#C9431D", "#FF5A2E"]}
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


# ------------------------------------------------------------------ data
def gql(query, **variables):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query, "variables": variables}).encode(),
                                 {"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]


def rest_count(q):
    req = urllib.request.Request("https://api.github.com/search/issues?per_page=1&q=" + urllib.parse.quote(q),
                                 headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(req))["total_count"]


CAL = """query($login:String!,$from:DateTime,$to:DateTime){user(login:$login){createdAt
 contributionsCollection(from:$from,to:$to){totalCommitContributions restrictedContributionsCount
 contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""


def fetch():
    import urllib.parse  # noqa: F401  (used by rest_count)
    now = dt.datetime.now(dt.timezone.utc)
    last = gql(CAL, login=LOGIN)["user"]
    weeks = [[(d["date"], d["contributionCount"], LEVEL[d["contributionLevel"]]) for d in w["contributionDays"]]
             for w in last["contributionsCollection"]["contributionCalendar"]["weeks"]]
    # every day since the account was created, for the all-time longest streak
    days = {}
    for y in range(int(last["createdAt"][:4]), now.year + 1):
        c = gql(CAL, login=LOGIN, **{"from": f"{y}-01-01T00:00:00Z", "to": (f"{y}-12-31T23:59:59Z" if y < now.year else now.strftime("%Y-%m-%dT%H:%M:%SZ"))})
        cc = c["user"]["contributionsCollection"]
        if y == now.year:
            year_commits = cc["totalCommitContributions"]
            year_total = cc["contributionCalendar"]["totalContributions"]
        for w in cc["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return dict(weeks=weeks, days=days, year=now.year, year_total=year_total, year_commits=year_commits,
                prs=rest_count(f"author:{LOGIN} type:pr"), merged=rest_count(f"author:{LOGIN} type:pr is:merged"),
                today=now.date().isoformat())


def demo():
    random.seed(7)
    today = dt.date(2026, 11, 8)
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)
    weeks, days, cur = [], {}, start
    while cur <= today:
        wk = []
        for _ in range(7):
            if cur > today:
                break
            n = 0 if random.random() < .35 else int(random.expovariate(.25)) + 1
            days[cur.isoformat()] = n
            wk.append((cur.isoformat(), n, min(4, (n + 2) // 3)))
            cur += dt.timedelta(days=1)
        weeks.append(wk)
    return dict(weeks=weeks, days=days, year=2026, year_total=1284, year_commits=972, prs=9, merged=6, today=today.isoformat())


def streaks(days, today):
    d = dt.date.fromisoformat(today)
    if days.get(today, 0) == 0:          # today isn't over yet; don't break the streak
        d -= dt.timedelta(days=1)
    cur = 0
    while days.get(d.isoformat(), 0) > 0:
        cur += 1; d -= dt.timedelta(days=1)
    best = run = 0
    for k in sorted(days):
        run = run + 1 if days[k] > 0 else 0
        best = max(best, run)
    return cur, best


# ------------------------------------------------------------------ drawing
def odometer(value, x, y, size, fill, delay, uid):
    """Rolling-digit number. Final state is the resting transform, so reduced-motion still shows the right value."""
    s = f"{value:,}"
    digit_gl = {str(i): glyphs(str(i), "serif", size)[0][0] for i in range(10)}
    adv = max(g[2] for g in digit_gl.values())
    comma_gl, _ = glyphs(",", "serif", size)
    step = size * 1.05
    out, css, cx = [], "", x
    out.append(f'<clipPath id="od{uid}"><rect x="{x - 4}" y="{y - size * .78:.0f}" width="{len(s) * adv + 10:.0f}" height="{size * .98:.0f}"/></clipPath><g clip-path="url(#od{uid})">')
    for i, ch in enumerate(s):
        if ch == ",":
            out.append(f'<path transform="translate({cx:.1f} {y})" d="{comma_gl[0][0]}" fill="{fill}"/>')
            cx += comma_gl[0][2]
            continue
        n = int(ch)
        spins = 10 + n                       # roll through a full turn, then land
        col = "".join(f'<path transform="translate({cx + (adv - digit_gl[str(k % 10)][2]) / 2:.1f} {y + k * step:.1f})" d="{digit_gl[str(k % 10)][0]}" fill="{fill}"/>'
                      for k in range(spins + 1))
        name = f"o{uid}_{i}"
        css += f"@keyframes {name}{{from{{transform:translateY(0);}}}}.{name}{{animation:{name} {1.6 + i * .25:.2f}s {EASE} {delay:.2f}s both;}}"
        out.append(f'<g class="{name}" style="transform:translateY({-spins * step:.1f}px)">{col}</g>')
        cx += adv
    out.append("</g>")
    return "".join(out), css, cx - x


def pulse(th, tn, data):
    W, H = 1200, 470
    ink, mute, acc = th["ink"], th["mute"], th["accent"]
    ramp = RAMP[tn]
    css = (".cell{animation:cell .6s " + EASE + " both;transform-box:fill-box;transform-origin:center;}"
           "@keyframes cell{from{opacity:0;transform:scale(.2);}}"
           ".ping{animation:ping 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center;}"
           "@keyframes ping{from{opacity:.9;transform:scale(1);}to{opacity:0;transform:scale(2.6);}}"
           ".fade{animation:fade 1s ease both;}@keyframes fade{from{opacity:0;}}")
    b = []
    upd = dt.date.fromisoformat(data["today"]).strftime("%d %b %Y").upper()
    b.append(T("CONTRIBUTIONS · LAST 12 MONTHS", 36, 40, "mono-md", 12.5, tracking=.08, fill=acc))
    b.append(T(f"REDRAWN DAILY FROM THE GITHUB API · {upd}", 1164, 40, "mono", 12, anchor="end", tracking=.08, fill=mute))

    cell, gap = 16, 4
    weeks = data["weeks"][-53:]
    x0 = 1164 - len(weeks) * (cell + gap) + gap
    y0 = 64
    for r, lab in [(1, "MON"), (3, "WED"), (5, "FRI")]:
        b.append(T(lab, 36, y0 + r * (cell + gap) + 13, "mono", 10.5, tracking=.06, fill=mute))
    last_month = None
    today_xy = None
    for c, wk in enumerate(weeks):
        for date, n, lvl in wk:
            r = dt.date.fromisoformat(date).isoweekday() % 7     # Sunday = row 0, like GitHub
            x, y = x0 + c * (cell + gap), y0 + r * (cell + gap)
            delay = .2 + c * .018 + r * .02
            b.append(f'<rect class="cell" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{ramp[lvl]}"><title>{n} on {date}</title></rect>')
            if date == data["today"]:
                today_xy = (x, y)
        m = dt.date.fromisoformat(wk[0][0]).strftime("%b").upper()
        if m != last_month and x0 + c * (cell + gap) < 1164 - 5 * 15 - 44 - 80:
            if last_month is not None:
                b.append(T(m, x0 + c * (cell + gap), y0 + 7 * (cell + gap) + 16, "mono", 10.5, tracking=.06, fill=mute))
            last_month = m
    if today_xy:
        x, y = today_xy
        b.append(f'<rect class="ping" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="none" stroke="{acc}" stroke-width="2"/>')
    # legend
    lx = 1164 - 5 * 15 - 44
    ly = y0 + 7 * (cell + gap) + 6
    b.append(T("LESS", lx - 8, ly + 10, "mono", 10.5, anchor="end", tracking=.06, fill=mute))
    for i, col in enumerate(ramp):
        b.append(f'<rect x="{lx + i * 15}" y="{ly}" width="11" height="11" rx="2" fill="{col}"/>')
    b.append(T("MORE", lx + 5 * 15 + 4, ly + 10, "mono", 10.5, tracking=.06, fill=mute))

    # stats row
    cur, best = streaks(data["days"], data["today"])
    stats = [(data["year_total"], f"CONTRIBUTIONS · {data['year']}"), (data["year_commits"], f"COMMITS · {data['year']}"),
             (data["merged"], "PULL REQUESTS MERGED"), (cur, "CURRENT STREAK · DAYS"), (best, "LONGEST STREAK · DAYS")]
    top = 282
    b.append(f'<line x1="36" y1="{top}" x2="1164" y2="{top}" stroke="{ink}" stroke-width="1.2"/>')
    colw = 1128 / 5
    for i, (v, lab) in enumerate(stats):
        x = 36 + i * colw
        if i:
            b.append(f'<line x1="{x:.0f}" y1="{top + 22}" x2="{x:.0f}" y2="{H - 26}" stroke="{th["rule"]}"/>')
        hot = i == 3 and cur > 0
        od, ocss, ow = odometer(v, x + (22 if i else 0), top + 112, 92, acc if hot else ink, .5 + i * .15, i)
        b.append(od); css += ocss
        if hot:
            b.append(f'<g class="fade" style="animation-delay:2.4s">{star(x + 22 + ow + 18, top + 52, 10, acc)}</g>')
        b.append(T(lab, x + (24 if i else 2), top + 152, "mono-md", 11.5, tracking=.08, fill=mute))
    alt = (f"Contributions in {data['year']}: {data['year_total']}. Commits: {data['year_commits']}. "
           f"Pull requests merged: {data['merged']}. Current streak: {cur} days. Longest streak: {best} days.")
    return svg(W, H, "".join(b), css, th, "Pulse — " + alt, grain=False)


if __name__ == "__main__":
    data = demo() if DEMO else fetch()
    os.makedirs(OUT, exist_ok=True)
    for tn, th in THEMES.items():
        with open(f"{OUT}/pulse-{tn}.svg", "w") as f:
            f.write(pulse(th, tn, data))
    print("pulse ok", {k: v for k, v in data.items() if k not in ("weeks", "days")})

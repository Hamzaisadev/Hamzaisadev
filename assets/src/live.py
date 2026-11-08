"""Hourly live layer for the profile README.

Runs in .github/workflows/live.yml (hourly, and whenever someone opens an issue or I answer one):
  * handles guestbook signatures, poll votes and AMA questions sent as issues
  * redraws the hero (Karachi time, sky, weather, seasonal palette) and every other static asset
  * redraws Pulse, the latest-commit card, "shipped this week", visitor counter, guestbook board and poll
  * rewrites the AMA block in README.md

Env: GH_TOKEN (PULSE_TOKEN or the workflow token), REPO_TOKEN (workflow token, for issue replies),
     GITHUB_REPOSITORY, GITHUB_EVENT_NAME, GITHUB_EVENT_PATH.
Local design work:  python3 live.py <outdir> --demo
"""
import datetime as dt, json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = next((a for a in sys.argv[1:] if not a.startswith("--")), os.path.join(HERE, ".."))
DEMO = "--demo" in sys.argv[1:] or os.environ.get("LIVE_DEMO") == "1"
sys.argv = [sys.argv[0], OUT]            # gen/pulse read their output dir from argv

import gen                                # noqa: E402
from gen import THEMES, EASE, svg, star, seasonal   # noqa: E402
from typeset import text as T, measure   # noqa: E402

LOGIN = "Hamzaisadev"
REPO = os.environ.get("GITHUB_REPOSITORY", f"{LOGIN}/{LOGIN}")
ROOT = os.path.join(OUT, "..")
DATA = os.path.join(OUT, "data")
os.makedirs(DATA, exist_ok=True)
KHI = dt.timezone(dt.timedelta(hours=5))
NOW = dt.datetime.now(dt.timezone.utc)

POLL_FILE = os.path.join(DATA, "poll.json")
DEFAULT_POLL = {"question": "What should I build next?",
                "options": ["A Curewell mobile app", "An open-source Next.js store starter",
                            "A Stash desktop app", "Something with AI agents"]}


# ------------------------------------------------------------------ GitHub helpers
def api(path, token_env="GH_TOKEN", method="GET", body=None):
    tok = os.environ.get(token_env) or os.environ.get("GH_TOKEN")
    req = urllib.request.Request("https://api.github.com" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"bearer {tok}", "Accept": "application/vnd.github+json",
                                          "User-Agent": "profile-live"})
    with urllib.request.urlopen(req, timeout=30) as r:
        txt = r.read()
        return json.loads(txt) if txt else {}


def safe(fn, default):
    try:
        return fn()
    except Exception as e:                # one failing source must never break the whole page
        print("warn:", fn.__name__ if hasattr(fn, "__name__") else fn, e)
        return default


def load(name, default):
    p = os.path.join(DATA, name)
    return json.load(open(p)) if os.path.exists(p) else default


def save(name, obj):
    json.dump(obj, open(os.path.join(DATA, name), "w"), indent=2, ensure_ascii=False)


def ago(ts):
    s = (NOW - dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds()
    for unit, n in (("DAY", 86400), ("HOUR", 3600), ("MINUTE", 60)):
        if s >= n:
            v = int(s // n)
            return v, unit + ("S" if v != 1 else "")
    return 0, "MINUTES"


FLAP_OK = re.compile(r"[^A-Z0-9 .,!?'&+@#:/()-]")


def flap_text(s, n):
    s = FLAP_OK.sub("", (s or "").upper().replace("\n", " "))
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > n:
        cut = s[:n + 1].rsplit(" ", 1)[0]
        s = cut if len(cut) >= n * .6 else s[:n]
    return s[:n]


# ------------------------------------------------------------------ issue events (guestbook / poll / AMA)
def handle_event():
    name = os.environ.get("GITHUB_EVENT_NAME", "")
    path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not path or not os.path.exists(path) or name not in ("issues", "issue_comment"):
        return
    ev = json.load(open(path))
    issue = ev.get("issue", {})
    n, title, user = issue.get("number"), issue.get("title", ""), issue.get("user", {}).get("login", "")
    kind = title.split(":", 1)[0].strip().lower()

    def reply(msg, close=True):
        api(f"/repos/{REPO}/issues/{n}/comments", "REPO_TOKEN", "POST", {"body": msg})
        if close:
            api(f"/repos/{REPO}/issues/{n}", "REPO_TOKEN", "PATCH", {"state": "closed", "state_reason": "completed"})

    if name == "issues" and ev.get("action") == "opened":
        if kind == "guestbook":
            reply(f"Thanks for signing, @{user}! Your name will appear on the guestbook board at https://github.com/{LOGIN} within a minute or two.")
        elif kind == "vote":
            reply(f"Vote counted, @{user}. Votes are one per person; voting again replaces your earlier choice. Live results are on https://github.com/{LOGIN}.")
        elif kind == "ama":
            reply(f"Thanks for the question, @{user}! I'll answer right here, and the answer gets pinned on my profile.", close=False)
    elif name == "issue_comment" and kind == "ama" and ev.get("comment", {}).get("user", {}).get("login", "").lower() == LOGIN.lower():
        api(f"/repos/{REPO}/issues/{n}", "REPO_TOKEN", "PATCH", {"state": "closed", "state_reason": "completed"})


def form_field(body, label):
    m = re.search(r"### " + re.escape(label) + r"\s*\n+(.*?)(?:\n### |\Z)", body or "", re.S)
    v = (m.group(1).strip() if m else "")
    return "" if v == "_No response_" else v


def issues_of(kind):
    out, page = [], 1
    while page <= 5:
        batch = api(f"/repos/{REPO}/issues?state=all&per_page=100&page={page}&sort=created&direction=desc", "REPO_TOKEN")
        if not batch:
            break
        out += [i for i in batch if "pull_request" not in i and i["title"].split(":", 1)[0].strip().lower() == kind]
        page += 1
    return out


# ------------------------------------------------------------------ data sources
def karachi_ctx():
    k = NOW.astimezone(KHI)
    ctx = dict(hour=k.hour + k.minute / 60, time=k.strftime("%I:%M %p").lstrip("0"))

    def weather():
        u = ("https://api.open-meteo.com/v1/forecast?latitude=24.86&longitude=67.0&current=temperature_2m"
             "&daily=sunrise,sunset&timezone=Asia%2FKarachi&forecast_days=1")
        w = json.load(urllib.request.urlopen(u, timeout=15))
        hm = lambda s: int(s[11:13]) + int(s[14:16]) / 60
        return dict(temp=f'{round(w["current"]["temperature_2m"])}°C', sunrise=hm(w["daily"]["sunrise"][0]), sunset=hm(w["daily"]["sunset"][0]))
    ctx.update(safe(weather, {}))
    return ctx, k.date()


def latest_commit():
    events = api(f"/users/{LOGIN}/events?per_page=50")
    for e in events:
        if e["type"] != "PushEvent":
            continue
        repo, private = e["repo"]["name"], not e.get("public", True)
        msg = ""
        commits = e.get("payload", {}).get("commits") or []
        if commits:
            msg = commits[-1].get("message", "")
        elif not private and e["payload"].get("head"):
            msg = safe(lambda: api(f"/repos/{repo}/commits/{e['payload']['head']}")["commit"]["message"], "")
        return dict(repo=repo.split("/")[1], private=private, message=msg.splitlines()[0] if msg else "", at=e["created_at"])
    return None


def shipped_week():
    since = (NOW - dt.timedelta(days=7)).date().isoformat()
    rows = []
    q = urllib.parse.quote(f"author:{LOGIN} type:pr is:merged merged:>={since}")
    for it in api(f"/search/issues?q={q}&per_page=5&sort=updated")["items"]:
        rows.append(dict(tag="PR MERGED", title=it["title"], repo=it["repository_url"].rsplit("/", 1)[1], at=it.get("closed_at") or it["updated_at"]))
    pushes = {}
    for e in api(f"/users/{LOGIN}/events?per_page=100"):
        if e["created_at"][:10] < since:
            continue
        r = e["repo"]["name"].split("/")[1]
        if e["type"] == "ReleaseEvent":
            rel = e["payload"].get("release", {})
            rows.append(dict(tag="RELEASE", title=rel.get("name") or rel.get("tag_name", ""), repo=r, at=e["created_at"]))
        elif e["type"] == "CreateEvent" and e["payload"].get("ref_type") == "repository":
            rows.append(dict(tag="NEW REPO", title=e["payload"].get("description") or r, repo=r, at=e["created_at"]))
        elif e["type"] == "PushEvent":
            p = pushes.setdefault(r, dict(n=0, at=e["created_at"], private=not e.get("public", True)))
            p["n"] += 1
    for r, p in sorted(pushes.items(), key=lambda kv: -kv[1]["n"])[:3]:
        rows.append(dict(tag="PUSHED", title=f'{p["n"]} push{"es" if p["n"] != 1 else ""} to {"a private repo" if p["private"] else r}',
                         repo="" if p["private"] else r, at=p["at"]))
    rows.sort(key=lambda x: x["at"], reverse=True)
    return rows[:5]


def visitors():
    """Profile views via komarev's image counter (embedded in the README). Every fetch from here also counts
    as a hit, so those self-hits are tracked and subtracted to keep the number honest."""
    st = load("visitors.json", {"self_hits": 0, "count": 0})
    svg_txt = urllib.request.urlopen(urllib.request.Request(f"https://komarev.com/ghpvc/?username={LOGIN.lower()}",
                                                            headers={"User-Agent": "profile-live"}), timeout=15).read().decode()
    nums = [int(x.replace(",", "")) for x in re.findall(r">\s*([\d,]+)\s*<", svg_txt)]
    st["self_hits"] += 1
    if nums:
        st["count"] = max(0, max(nums) - st["self_hits"])
    st.setdefault("since", NOW.strftime("%b %Y").upper())
    save("visitors.json", st)
    return st


def guestbook():
    rows = []
    for i in issues_of("guestbook"):
        msg = form_field(i.get("body"), "Leave a short message") or i["title"].split(":", 1)[1]
        rows.append(dict(user=i["user"]["login"], msg=msg))
    save("guestbook.json", rows[:50])
    return rows


def poll():
    cfg = load("poll.json", DEFAULT_POLL)
    save("poll.json", cfg)
    latest = {}
    for i in reversed(issues_of("vote")):                    # oldest first, so newer votes overwrite
        choice = form_field(i.get("body"), "Your pick")
        if choice in cfg["options"]:
            latest[i["user"]["login"].lower()] = choice
    counts = {o: 0 for o in cfg["options"]}
    for c in latest.values():
        counts[c] += 1
    return cfg["question"], counts


def ama():
    out = []
    for i in issues_of("ama"):
        if i["comments"] == 0:
            continue
        comments = api(f"/repos/{REPO}/issues/{i['number']}/comments?per_page=100", "REPO_TOKEN")
        mine = [c for c in comments if c["user"]["login"].lower() == LOGIN.lower()]
        if not mine:
            continue
        q = form_field(i.get("body"), "Your question") or i["title"].split(":", 1)[1]
        out.append(dict(q=q, a=mine[-1]["body"], user=i["user"]["login"], url=i["html_url"]))
        if len(out) == 3:
            break
    return out


# ------------------------------------------------------------------ drawing
LIVE_CSS = (".fade{animation:fade 1s ease both;}@keyframes fade{from{opacity:0;}}"
            ".dot{animation:dot 1.6s ease-in-out infinite;}@keyframes dot{50%{opacity:.2;}}"
            f".fp{{animation:fp .5s {EASE} both;transform-box:fill-box;transform-origin:center;}}@keyframes fp{{0%{{transform:scaleY(0);}}60%{{transform:scaleY(1.08);}}}}"
            f".bar{{animation:bar 1.6s {EASE} both;transform-box:fill-box;transform-origin:left;}}@keyframes bar{{from{{transform:scaleX(0);}}}}")


def live_tag(th, x, y, text, anchor="start"):
    w = measure(text, "mono-md", 12, .08)
    x0 = x if anchor == "start" else x - w - 18
    return (f'<circle class="dot" cx="{x0 + 5}" cy="{y - 4}" r="4.5" fill="{th["accent"]}"/>'
            + T(text, x0 + 18, y, "mono-md", 12, tracking=.08, fill=th["mute"]))


def flap(th, x, y, text, cols, color, delay0=0.0, tw=30, th_=44):
    out = []
    for c in range(cols):
        ch = text[c] if c < len(text) else " "
        cx = x + c * (tw + 4)
        out.append(f'<g class="fp" style="animation-delay:{delay0 + c * .03:.2f}s"><rect x="{cx}" y="{y}" width="{tw}" height="{th_}" rx="3" fill="{th["tile"]}"/>')
        if ch.strip():
            out.append(T(ch, cx + tw / 2, y + th_ * .68, "mono-md", th_ * .48, anchor="middle", fill=color))
        out.append(f'<line x1="{cx}" y1="{y + th_ / 2}" x2="{cx + tw}" y2="{y + th_ / 2}" stroke="{th["paper"]}" stroke-opacity=".5"/></g>')
    return "".join(out)


def card_commit(th, c):
    W, H = 1200, 230
    b = [f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" fill="none" stroke="{th["rule"]}" stroke-width="1.5"/>',
         T("LATEST COMMIT", 40, 52, "mono-md", 13, tracking=.08, fill=th["accent"]),
         live_tag(th, 1160, 52, "LIVE · REDRAWN HOURLY", "end")]
    if not c:
        b.append(T("Nothing public pushed lately.", 36, 150, "serif", 64, fill=th["ink"]))
        return svg(W, H, "".join(b), LIVE_CSS, th, "Latest commit: none recently", grain=False)
    v, unit = ago(c["at"])
    big = str(v)
    bw = measure(big, "serif", 120)
    b.append(T(big, 1160 - 150 - bw, 170, "serif", 120, fill=th["ink"]))
    b.append(T(unit, 1160, 128, "mono-md", 13, anchor="end", tracking=.1, fill=th["ink"]))
    b.append(T("AGO", 1160, 150, "mono-md", 13, anchor="end", tracking=.1, fill=th["mute"]))
    repo = "a private repo" if c["private"] else c["repo"]
    maxw = 1160 - 150 - bw - 60 - 40
    size = 64
    while measure(repo, "serif-it" if c["private"] else "serif", size) > maxw and size > 36:
        size -= 4
    b.append(f'<g class="fade">{T(repo, 36, 132, "serif-it" if c["private"] else "serif", size, fill=th["ink"])}</g>')
    msg = "Message hidden — private work." if c["private"] else (c["message"] or "")
    while msg and measure(msg, "sans", 20) > maxw:
        msg = msg[:-2].rstrip() + "…" if not msg.endswith("…") else msg[:-2].rstrip() + "…"
    b.append(f'<g class="fade" style="animation-delay:.3s">{T(msg, 40, 182, "sans", 20, fill=th["mute"])}</g>')
    alt = f"Latest commit: {repo}, {v} {unit.lower()} ago" + (f" — {c['message']}" if c["message"] and not c["private"] else "")
    return svg(W, H, "".join(b), LIVE_CSS, th, alt, grain=False)


def card_shipped(th, rows):
    rh = 58
    W, H = 1200, 96 + max(1, len(rows)) * rh + 18
    start = (NOW - dt.timedelta(days=6)).astimezone(KHI).strftime("%d %b").upper()
    end = NOW.astimezone(KHI).strftime("%d %b").upper()
    b = [f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" fill="none" stroke="{th["rule"]}" stroke-width="1.5"/>',
         T(f"SHIPPED THIS WEEK · {start} – {end}", 40, 52, "mono-md", 13, tracking=.08, fill=th["accent"]),
         live_tag(th, 1160, 52, "AUTO-LISTED FROM GITHUB", "end"),
         f'<line x1="40" y1="78" x2="1160" y2="78" stroke="{th["ink"]}" stroke-width="1.2"/>']
    if not rows:
        b.append(T("A quiet week in public. Heads down on something.", 40, 78 + 40, "serif-it", 32, fill=th["mute"]))
    for i, r in enumerate(rows):
        y = 78 + i * rh
        tw_ = measure(r["tag"], "mono-md", 11.5, .08)
        b.append(f'<g class="fade" style="animation-delay:{.2 + i * .12:.2f}s">')
        b.append(f'<rect x="40" y="{y + 16}" width="{tw_ + 22:.0f}" height="26" rx="13" fill="{th["accent"] if r["tag"] in ("PR MERGED", "RELEASE") else "none"}" stroke="{th["accent"]}" stroke-width="1.2"/>')
        b.append(T(r["tag"], 51, y + 33.5, "mono-md", 11.5, tracking=.08, fill=th["onaccent"] if r["tag"] in ("PR MERGED", "RELEASE") else th["accent"]))
        title = r["title"]
        while measure(title, "sans", 19) > 700:
            title = title[:-2].rstrip() + "…"
        b.append(T(title, 210, y + 36, "sans", 19, fill=th["ink"]))
        when = dt.datetime.fromisoformat(r["at"].replace("Z", "+00:00")).astimezone(KHI).strftime("%a").upper()
        b.append(T((r["repo"] + " · " if r["repo"] else "") + when, 1160, y + 35, "mono", 12, anchor="end", tracking=.06, fill=th["mute"]))
        b.append(f'<line x1="40" y1="{y + rh}" x2="1160" y2="{y + rh}" stroke="{th["rule"]}"/></g>')
    alt = "Shipped this week: " + ("; ".join(f'{r["tag"].lower()} — {r["title"]}' for r in rows) or "nothing public")
    return svg(W, H, "".join(b), LIVE_CSS, th, alt, grain=False)


def card_visitors(th, st):
    W, H = 1200, 150
    digits = f'{st["count"]:07d}'
    b = [T("PROFILE VISITS", 36, 64, "mono-md", 14, tracking=.1, fill=th["ink"]),
         T(f'COUNTED SINCE {st.get("since", "")} · UPDATED HOURLY', 36, 88, "mono", 11.5, tracking=.08, fill=th["mute"])]
    x0 = 1164 - 7 * 54 + 6
    for i, d in enumerate(digits):
        b.append(flap(th, x0 + i * 54, 30, d, 1, th["accent"] if i >= 7 - len(str(st["count"])) else th["mute"], .2 + i * .08, tw=48, th_=72))
    return svg(W, H, "".join(b), LIVE_CSS, th, f'Profile visits: {st["count"]}', grain=False)


def board_guestbook(th, rows):
    rows = rows[:5]
    W = 1200
    H = 74 + 5 * 58 + 20
    b = [T("GUESTBOOK · LATEST SIGNATURES", 36, 40, "mono-md", 12.5, tracking=.08, fill=th["accent"]),
         live_tag(th, 1164, 40, f"{len(rows)} OF THE LATEST" if rows else "BE THE FIRST", "end")]
    for r in range(5):
        y = 70 + r * 58
        if r < len(rows):
            name = flap_text("@" + rows[r]["user"], 14)
            msg = flap_text(rows[r]["msg"], 21)
        else:
            name, msg = ("YOUR NAME HERE", "SIGN BELOW") if r == len(rows) else ("", "")
        b.append(flap(th, 36, y, name, 14, th["accent"], .3 + r * .2, tw=26, th_=44))
        b.append(flap(th, 36 + 14 * 30 + 26, y, msg, 21, th["tiletext"], .5 + r * .2, tw=28, th_=44))
    alt = "Guestbook: " + ("; ".join(f'@{r["user"]}: {r["msg"]}' for r in rows) or "no signatures yet")
    return svg(W, H, "".join(b), LIVE_CSS, th, alt, grain=False)


def card_poll(th, question, counts):
    total = sum(counts.values())
    rh = 66
    W, H = 1200, 150 + len(counts) * rh
    b = [T("POLL · ONE VOTE PER PERSON", 36, 40, "mono-md", 12.5, tracking=.08, fill=th["accent"]),
         live_tag(th, 1164, 40, f"{total} VOTE{'S' if total != 1 else ''} · LIVE", "end"),
         T(question, 32, 112, "serif", 60, fill=th["ink"])]
    top = max(counts.values()) if total else 0
    for i, (opt, n) in enumerate(counts.items()):
        y = 146 + i * rh
        pct = n / total if total else 0
        lead = total and n == top
        b.append(T(opt, 36, y + 24, "sans", 19, fill=th["ink"]))
        b.append(T(f"{round(pct * 100)}%  ·  {n}", 1164, y + 24, "mono-md", 13, anchor="end", tracking=.06, fill=th["accent"] if lead else th["mute"]))
        b.append(f'<rect x="36" y="{y + 36}" width="1128" height="12" rx="6" fill="{th["panel"]}"/>')
        if n:
            b.append(f'<rect class="bar" style="animation-delay:{.3 + i * .15:.2f}s" x="36" y="{y + 36}" width="{max(12, 1128 * pct):.0f}" height="12" rx="6" fill="{th["accent"] if lead else th["ink"]}"/>')
    alt = f"Poll: {question} " + "; ".join(f"{o}: {n} votes" for o, n in counts.items())
    return svg(W, H, "".join(b), LIVE_CSS, th, alt, grain=False)


def ama_markdown(items):
    if not items:
        return ("<p align=\"center\"><sub>No questions answered yet. Ask the first one.</sub></p>")
    clean = lambda s, n: re.sub(r"[<>]", "", s).strip()[:n]
    parts = []
    for it in items:
        a = re.sub(r"<!--.*?-->", "", it["a"], flags=re.S).strip()
        a = "\n> ".join(a.splitlines())
        parts.append(f"> **Q · [@{clean(it['user'], 39)}](https://github.com/{clean(it['user'], 39)}):** {clean(it['q'], 240)}\n>\n> {a}\n>\n> <sub>[Thread ↗]({it['url']})</sub>")
    return "\n\n".join(parts)


# ------------------------------------------------------------------ demo data
def demo_data():
    return dict(
        commit=dict(repo="AnyRef", private=False, message="Add reference graph view with keyboard navigation", at=(NOW - dt.timedelta(hours=3)).isoformat()),
        shipped=[dict(tag="PR MERGED", title="Offline sync for medication reminders", repo="Curewell", at=(NOW - dt.timedelta(days=1)).isoformat()),
                 dict(tag="RELEASE", title="v1.2 — clipboard history", repo="Stash", at=(NOW - dt.timedelta(days=3)).isoformat()),
                 dict(tag="PUSHED", title="14 pushes to AnyRef", repo="AnyRef", at=(NOW - dt.timedelta(hours=3)).isoformat())],
        visitors={"count": 1287, "since": "NOV 2026"},
        guestbook=[dict(user="octocat", msg="Love the split-flap board!"), dict(user="sara-dev", msg="Hire this man"),
                   dict(user="karachi-coder", msg="Salam from Clifton")],
        poll=(DEFAULT_POLL["question"], dict(zip(DEFAULT_POLL["options"], [12, 5, 3, 9]))),
        ama=[dict(q="How do you price a small business website?", a="By the outcome they need, not by pages. I scope the goal first, then quote a fixed price.", user="octocat", url="https://github.com")])


# ------------------------------------------------------------------ main
def main():
    if not DEMO:
        safe(handle_event, None)
    ctx, today = karachi_ctx()
    season = gen.build(OUT, ctx, today)
    themes = seasonal(THEMES, season)

    if DEMO:
        d = demo_data()
    else:
        d = dict(commit=safe(latest_commit, None), shipped=safe(shipped_week, []),
                 visitors=safe(visitors, load("visitors.json", {"count": 0, "since": NOW.strftime("%b %Y").upper()})),
                 guestbook=safe(guestbook, load("guestbook.json", [])),
                 poll=safe(poll, (DEFAULT_POLL["question"], {o: 0 for o in DEFAULT_POLL["options"]})),
                 ama=safe(ama, None))
        import pulse
        pdata = safe(pulse.fetch, None)
        if pdata:
            for tn, th in themes.items():
                open(f"{OUT}/pulse-{tn}.svg", "w").write(pulse.pulse(th, tn, pdata))

    for tn, th in themes.items():
        files = {"live-commit": card_commit(th, d["commit"]), "live-shipped": card_shipped(th, d["shipped"]),
                 "live-visitors": card_visitors(th, d["visitors"]), "live-guestbook": board_guestbook(th, d["guestbook"]),
                 "live-poll": card_poll(th, *d["poll"])}
        for k, v in files.items():
            open(f"{OUT}/{k}-{tn}.svg", "w").write(v)

    if d["ama"] is not None:
        readme = os.path.join(ROOT, "README.md")
        if os.path.exists(readme):
            md = open(readme).read()
            md2 = re.sub(r"<!--AMA:START-->.*?<!--AMA:END-->", "<!--AMA:START-->\n" + ama_markdown(d["ama"]) + "\n<!--AMA:END-->", md, flags=re.S)
            if md2 != md:
                open(readme, "w").write(md2)
    print("live ok", "season:", season and season["name"], "| ctx:", ctx)


if __name__ == "__main__":
    main()

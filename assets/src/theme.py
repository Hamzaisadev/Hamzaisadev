"""Force the README's images to light, dark, or auto (follow the viewer's GitHub theme).

Run by .github/workflows/theme.yml when someone opens an issue titled "theme: <mode>".
Usage: python3 theme.py <light|auto|dark> [github-username]
"""
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
README = os.path.join(ROOT, "README.md")
STATE = os.path.join(ROOT, ".github", "theme.json")
MODES = ("light", "auto", "dark")

mode = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "auto"
user = re.sub(r"[^A-Za-z0-9-]", "", sys.argv[2])[:39] if len(sys.argv) > 2 else ""
if mode not in MODES:
    raise SystemExit(f"unknown mode {mode!r}")

state = json.load(open(STATE)) if os.path.exists(STATE) else {"mode": "auto", "by": "", "count": 0}
state.update(mode=mode, by=user, count=state.get("count", 0) + 1)

dark_variant = "light" if mode == "light" else "dark"   # what viewers in GitHub dark mode get
light_variant = "dark" if mode == "dark" else "light"   # what viewers in GitHub light mode get
VARIANT = re.compile(r"-(light|dark)(\.(?:svg|gif))")


def fix_picture(m):
    block = m.group(0)
    block = re.sub(r'(<source media="\(prefers-color-scheme: dark\)" srcset="[^"]*)', lambda s: VARIANT.sub(rf"-{dark_variant}\2", s.group(1)), block)
    block = re.sub(r'(<source media="\(prefers-color-scheme: light\)" srcset="[^"]*)', lambda s: VARIANT.sub(rf"-{light_variant}\2", s.group(1)), block)
    block = re.sub(r'(<img src="[^"]*)', lambda s: VARIANT.sub(rf"-{light_variant}\2", s.group(1)), block)
    return block


md = open(README).read()
md = re.sub(r"<picture>.*?</picture>", fix_picture, md, flags=re.S)
md = re.sub(r"seg-(light|auto|dark)-(on|off)", lambda s: f"seg-{s.group(1)}-{'on' if s.group(1) == mode else 'off'}", md)

desc = {"auto": "follows your GitHub setting", "light": "forced light for everyone", "dark": "forced dark for everyone"}[mode]
credit = f" · last flipped by <a href=\"https://github.com/{user}\">@{user}</a>" if user else ""
line = (f"<!--THEME:START-->Theme: <b>{mode}</b> — {desc}{credit} · flipped {state['count']} "
        f"time{'s' if state['count'] != 1 else ''}. Pick one above; GitHub Actions repaints the page.<!--THEME:END-->")
md = re.sub(r"<!--THEME:START-->.*?<!--THEME:END-->", line, md, flags=re.S)

open(README, "w").write(md)
json.dump(state, open(STATE, "w"), indent=2)
print("theme ->", mode, "by", user or "-")

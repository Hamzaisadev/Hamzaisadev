"""Screenshot each live project (desktop + mobile, full page) for the device frames on the project cards.
Run weekly by .github/workflows/shots.yml.  Usage: python3 shots.py <assets dir>"""
import os, sys, io
from PIL import Image
from playwright.sync_api import sync_playwright

OUT = os.path.join(sys.argv[1] if len(sys.argv) > 1 else "..", "shots")
os.makedirs(OUT, exist_ok=True)
SITES = {
    "curewell": "https://curewell-ai.vercel.app",
    "gadighar": "https://gadi-ghar.vercel.app",
    "snapistan": "https://snapistan.vercel.app",
    "linkwhiz": "https://linkwhize.netlify.app/",
    "almuzzammil": "https://al-muzzammil.vercel.app",
    "79stauto": "https://79st-auto-website.vercel.app",
}
SPECS = {"desktop": dict(viewport={"width": 1440, "height": 900}, device_scale_factor=1, out_w=1000, max_h=3600),
         "mobile": dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, out_w=420, max_h=4200)}


def save(png, path, out_w, max_h):
    im = Image.open(io.BytesIO(png)).convert("RGB")
    im = im.resize((out_w, int(im.height * out_w / im.width)), Image.LANCZOS)
    im.crop((0, 0, out_w, min(im.height, max_h))).save(path, "JPEG", quality=80, optimize=True, progressive=True)


with sync_playwright() as p:
    browser = p.chromium.launch()
    for slug, url in SITES.items():
        for kind, spec in SPECS.items():
            opts = {k: v for k, v in spec.items() if k not in ("out_w", "max_h")}
            ctx = browser.new_context(**opts, color_scheme="light", reduced_motion="reduce")
            page = ctx.new_page()
            try:
                resp = page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                dead = (resp is None or resp.status >= 400
                        or "page doesn't exist" in page.content().lower() or "page not found" in page.title().lower())
                if dead:
                    # a 404 in a device frame looks worse than the drawn motif; drop the old shot too
                    for k in SPECS:
                        f = os.path.join(OUT, f"{slug}-{k}.jpg")
                        if os.path.exists(f):
                            os.remove(f)
                    print("dead", slug, resp and resp.status)
                    break
                # nudge lazy-loaded sections, then return to top
                page.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,120))}scrollTo(0,0)}")
                page.wait_for_timeout(1200)
                save(page.screenshot(full_page=True), os.path.join(OUT, f"{slug}-{kind}.jpg"), spec["out_w"], spec["max_h"])
                desc = page.evaluate("()=>(document.querySelector('meta[name=description]')||{}).content||''")
                h1 = page.evaluate("()=>[...document.querySelectorAll('h1,h2')].slice(0,3).map(e=>e.innerText.trim()).join(' | ')")
                print("ok", slug, kind, "| title:", page.title(), "| desc:", desc[:160], "| h:", h1[:200].replace("\n", " "))
            except Exception as e:
                print("skip", slug, kind, e)          # keep last week's shot, or the drawn motif
            finally:
                ctx.close()
    browser.close()

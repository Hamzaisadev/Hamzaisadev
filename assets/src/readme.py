"""Assemble README.md. Preserves the WakaTime block from the current README."""
import re, sys

SRC = sys.argv[1]       # existing README (for the waka block)
DST = sys.argv[2]

waka = re.search(r"<!--START_SECTION:waka-->.*?<!--END_SECTION:waka-->", open(SRC).read(), re.S).group(0)


def pic(name, alt, width="100%", href=None, ext="svg"):
    tag = (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Hamzaisadev/Hamzaisadev/main/assets/{name}-dark.{ext}" />\n'
           f'  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Hamzaisadev/Hamzaisadev/main/assets/{name}-light.{ext}" />\n'
           f'  <img src="./assets/{name}-light.{ext}" width="{width}" alt="{alt}" />\n</picture>')
    return f'<a href="{href}">\n{tag}\n</a>' if href else tag


def links(*pairs):
    return "&nbsp;&nbsp;·&nbsp;&nbsp;".join(f'<a href="{u}"><b>{t}</b></a>' for t, u in pairs)


STREAK = ("https://streak-stats.demolab.com?user=Hamzaisadev&hide_border=true&border_radius=0"
          "&background={bg}&ring={ac}&fire={ac}&currStreakNum={ink}&sideNums={ink}&currStreakLabel={ac}"
          "&sideLabels={mute}&dates={mute}&stroke={rule}")
L = dict(bg="F3EFE7", ac="FF4A1C", ink="141311", mute="6E685E", rule="D6CFC2")
D = dict(bg="0E0E0D", ac="FF5A2E", ink="EEE9DF", mute="8D877C", rule="2B2926")
SNAKE = "https://raw.githubusercontent.com/Hamzaisadev/Hamzaisadev/output/snake-{}.svg"

md = f"""<!-- Profile README for @Hamzaisadev. Every image in /assets is generated (see /assets/README.md). -->

<div align="center">

{pic("hero", "Hamza Ishaq — full-stack developer in Karachi. Open to front-end roles and freelance builds.", href="https://hamzaisadev.netlify.app")}

<br />

{links(("Portfolio", "https://hamzaisadev.netlify.app"), ("LinkedIn", "https://www.linkedin.com/in/hamzaisadev/"), ("X", "https://twitter.com/hamzaisadev"), ("YouTube", "https://youtube.com/channel/UCPR0FgOTackPp82nMyPqf5A"), ("Email", "mailto:hamzaisadev@gmail.com"))}

</div>

<br />

{pic("monogram", "A dithered 3D H, slowly turning", width="220", ext="gif").replace("<img ", '<img align="right" ')}

### Hi, I'm Hamza.

I'm a full-stack developer in Karachi and the founder of **Albatix**, where I build websites and online stores for businesses that need a site that sells, not just a site that exists.

I judge my work by whether it brings in more customers, sales or profit, not by how much code I wrote. I use AI heavily, but I still need to understand the code well enough to direct it, check it and debug it.

Mostly **Next.js, React and TypeScript**, backed by **Postgres or Supabase**. I'm open to **front-end roles** (Karachi or remote) and to **freelance builds**.

<br clear="right" />
<br />

{pic("h01", "01 — Selected work")}

{pic("card-curewell", "Curewell — personal health OS: prescription OCR, meal-timed doses, lab tracking. Hackathon national finalist.", href="https://curewell-gamma.vercel.app")}

<p align="center">{links(("Live ↗", "https://curewell-gamma.vercel.app"), ("Source", "https://github.com/Hamzaisadev/Curewell"))}</p>

{pic("card-stash", "Stash — file sharing, screen casting and clipboard sync between devices, no login.", href="https://stash-ed.vercel.app")}

<p align="center">{links(("Live ↗", "https://stash-ed.vercel.app"), ("Source", "https://github.com/Hamzaisadev/Stash"))}</p>

{pic("card-gadighar", "Gadi Ghar — full-stack car marketplace for Pakistan.", href="https://gadi-ghar.vercel.app")}

<p align="center">{links(("Live ↗", "https://gadi-ghar.vercel.app"), ("Source", "https://github.com/Hamzaisadev/gadi-ghar"))}</p>

<table>
  <tr>
    <td width="50%" valign="top">
{pic("card-snapistan", "Snapistan — social network built with Next.js, Prisma and PostgreSQL.", href="https://snapistan.vercel.app")}
<p align="center">{links(("Live ↗", "https://snapistan.vercel.app"), ("Source", "https://github.com/Hamzaisadev/Snapistan"))}</p>
    </td>
    <td width="50%" valign="top">
{pic("card-devshot", "DevShot — Chrome extension for page captures and device mockups.", href="https://github.com/Hamzaisadev/DevShot")}
<p align="center">{links(("Source", "https://github.com/Hamzaisadev/DevShot"), ("Download zip", "https://codeload.github.com/Hamzaisadev/DevShot/zip/refs/heads/main"))}</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
{pic("card-linkwhiz", "LinkWhiz — URL shortener.", href="https://linkwhize.netlify.app/")}
<p align="center">{links(("Live ↗", "https://linkwhize.netlify.app/"), ("Source", "https://github.com/Hamzaisadev/LinkWhiz"))}</p>
    </td>
    <td width="50%" valign="top">
{pic("card-vault", "Daily Dev Vault — automated daily deep dives on systems design.", href="https://github.com/Hamzaisadev/daily-dev-vault")}
<p align="center">{links(("Read the vault", "https://github.com/Hamzaisadev/daily-dev-vault"),)}</p>
    </td>
  </tr>
</table>

<details>
<summary><b>From the archive</b> — older and smaller builds</summary>
<br />

| Project | What it is | Stack | Links |
| :-- | :-- | :-- | :-- |
| **PennyWise** | Personal budgeting with expense breakdowns | React, React Router | [Live](https://pennywisse.netlify.app/) · [Repo](https://github.com/Hamzaisadev/PennyWise) |
| **Vidiyo** | Video discovery and sharing | React, REST APIs | [Live](https://vidiyoo.netlify.app) · [Repo](https://github.com/Hamzaisadev/Vidiyo) |
| **SmartPress** | WordPress plugin that compresses images and serves modern formats | PHP, WordPress | [Repo](https://github.com/Hamzaisadev/smartpress-image-optimizer) |
| **Sabrina** | A chat-style AI assistant | JavaScript | [Repo](https://github.com/Hamzaisadev/Sabrina-Ai-Assistant) |
| **JavaScript Lab** | Small vanilla JS apps, one concept each | HTML, CSS, JS | [Live](https://hamzaisadev.github.io/Java-Script-Projects/) · [Repo](https://github.com/Hamzaisadev/Java-Script-Projects) |
| **Riwayat** | Men's traditional clothing store | Next.js, Tailwind | [Portfolio](https://hamzaisadev.netlify.app) |
| **Shoeaholic** | Footwear store with SEO-first product structure | Next.js | [Portfolio](https://hamzaisadev.netlify.app) |

</details>

<br />

{pic("h02", "02 — Right now")}

{pic("now", "Now building: AnyRef. Latest: Curewell, hackathon national finalist. Open to front-end roles. Taking on freelance builds. Based in Karachi, UTC+5.")}

<br />

{pic("h03", "03 — Toolbox")}

{pic("toolbox", "Interface: Next.js, React, TypeScript, Tailwind. Server: Node.js, Express, Prisma, REST. Data: PostgreSQL, Supabase, MongoDB. AI: Gemini, Vision OCR, LLM workflows. Shipping: Vercel, GitHub Actions, Vitest, Python.")}

<br />

{pic("h04", "04 — Pulse")}

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{SNAKE.format("dark")}" />
  <source media="(prefers-color-scheme: light)" srcset="{SNAKE.format("light")}" />
  <img src="{SNAKE.format("light")}" width="100%" alt="A snake eating my contribution graph" />
</picture>

<br /><br />

<a href="https://git.io/streak-stats">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{STREAK.format(**D)}" />
  <source media="(prefers-color-scheme: light)" srcset="{STREAK.format(**L)}" />
  <img src="{STREAK.format(**L)}" width="560" alt="GitHub contribution streak" />
</picture>
</a>

</div>

<details>
<summary><b>WakaTime</b> — hours, languages and editors, updated daily</summary>
<br />

{waka}

</details>

<br />

{pic("h05", "05 — Work with me")}

{pic("work", "Work with me. For teams hiring: front-end roles, React, Next.js, TypeScript, Karachi or remote, CV on request. For businesses: websites, online stores and landing pages through Albatix.")}

<p align="center">
<a href="https://github.com/Hamzaisadev/Hamzaisadev/issues/new?template=start-a-project.yml">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Hamzaisadev/Hamzaisadev/main/assets/btn-project-dark.svg" />
  <img src="./assets/btn-project-light.svg" height="52" alt="Start a project" />
</picture>
</a>
&nbsp;&nbsp;
<a href="mailto:hamzaisadev@gmail.com?subject=Front-end%20role%20%E2%80%94%20CV%20request">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Hamzaisadev/Hamzaisadev/main/assets/btn-cv-dark.svg" />
  <img src="./assets/btn-cv-light.svg" height="52" alt="Request my CV" />
</picture>
</a>
</p>

<p align="center"><sub>“Start a project” opens a short brief form here on GitHub: goal, pages, budget and timeline. Prefer private? Email works too.</sub></p>

<br />

{pic("footer", "Got a business problem? Let's ship the fix. Email hamzaisadev@gmail.com", href="mailto:hamzaisadev@gmail.com")}
"""
open(DST, "w").write(md)
print("ok")

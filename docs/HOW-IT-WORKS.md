# How my GitHub README redraws itself

My GitHub profile looks like a small website: a hero with the time and sky over Karachi, a split-flap status board, a guestbook, a live poll, and project cards whose screens scroll through the real apps. No server runs any of it. It's plain SVG files, redrawn by GitHub Actions.

Here's how it works, and what GitHub doesn't let you do.

## The constraint

A GitHub README is markdown with a small whitelist of HTML. No JavaScript, no `<style>`, no forms, no iframes. You can't have a button that *does* something. You can only have a link or an image.

But an SVG loaded as an image keeps its own internal CSS animations. That's the loophole everything here uses: every "component" is an SVG that animates itself, and the README just shows images.

## 1. Type that looks the same everywhere

SVGs loaded as images can't use web fonts, so text would fall back to whatever font the visitor has. Instead, a Python script shapes every string with HarfBuzz and converts each letter to vector outlines. Instrument Serif, Geist, Noto Nastaliq Urdu (for حمزہ) and a script face for the signature all render identically on every device.

Each glyph is its own path, which is what makes the letter-by-letter reveals and the rolling odometer digits possible.

## 2. Light and dark

Every asset is generated twice. The README uses `<picture>` with `prefers-color-scheme`, so visitors get the version that matches their GitHub theme.

## 3. The hourly redraw

One workflow, `live.yml`, runs every hour. It:

- reads the Karachi time and weather (Open-Meteo) and moves the sun or moon along the arc in the hero
- checks the Islamic calendar and switches the palette for Ramadan, Eid, and 14 August
- pulls my contribution calendar from the GitHub GraphQL API and redraws the heatmap and streaks
- finds my latest push and everything I shipped this week (merged PRs, releases, new repos)
- regenerates every SVG and commits only if something changed

## 4. Making it interactive without JavaScript

The only way a visitor can trigger code is by opening an issue. So the guestbook, the poll and Ask Me Anything are GitHub issue forms. When one is submitted, the same workflow:

- reads the form fields
- updates the board, poll or AMA block
- replies to the issue and closes it

Votes are deduplicated per GitHub account. AMA answers are just my comments on the issue; the workflow pins the latest three into the README.

## 5. Real screenshots

A second workflow runs weekly. It opens each live project in a headless Chromium (Playwright), takes desktop and mobile full-page screenshots, and the generator embeds them inside device frames. Inside each card, the laptop and phone screens slowly scroll through the actual page.

## 6. Counting visitors honestly

GitHub doesn't tell profile owners how many people view their profile. A tiny counter image is embedded in the page; the hourly job reads its total and subtracts its own requests so the number on the split-flap board isn't inflated.

## What I'd tell anyone copying this

- **Respect reduced motion.** Every SVG ships with a `prefers-reduced-motion` rule, and every animation's resting state is the final frame, so nothing is hidden when motion is off.
- **One failing API shouldn't break the page.** Each data source is wrapped so it falls back to the last good value.
- **Keep the copy honest.** No skill-percentage bars, no inflated numbers. Live data is more convincing than adjectives.

All the source is in [`assets/src`](../assets/src).

#!/usr/bin/env python3
"""Generate entry-led Nazar Instagram assets from realistic observation JSON."""

from __future__ import annotations

import csv
import html
import json
import subprocess
import tempfile
import time
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/nazar-entry-examples.json"
POSTS = ROOT / "content/posts"
STORIES = ROOT / "content/stories"
CAPTIONS = ROOT / "content/captions.csv"
CHROME = "/usr/local/bin/google-chrome"

SENSE_COLORS = {
    "sight": "#085041",
    "sound": "#534AB7",
    "smell": "#BA7517",
    "taste": "#D4537E",
    "touch": "#D85A30",
    "feeling": "#1D9E75",
}


def wrap(text: str, width: int) -> str:
    lines = textwrap.wrap(text, width=width, break_long_words=False)
    return "<br>".join(html.escape(line) for line in lines)


def clean_filename(path: Path) -> None:
    path.unlink(missing_ok=True)


def page(item: dict, kind: str) -> str:
    is_story = kind == "story"
    width, height = (1080, 1920) if is_story else (1080, 1350)
    design = item.get("shareCardDesign", {})
    palette = design.get("palette", {})
    background = palette.get("background", "#F7F4EF")
    ink = palette.get("text", "#1C1A17")
    muted = palette.get("muted", "#B0A89E")
    accent = palette.get("accent") or SENSE_COLORS.get(item.get("sense"), "#085041")
    entry = item["entry"]
    label = item["label"].lower()
    sense = item.get("sense", "noticing")
    texture = design.get("texture", "paper grain")

    phone_width = 760 if is_story else 790
    phone_height = 1160 if is_story else 860
    phone_top = 330 if is_story else 220
    entry_size = 50 if is_story else 43
    entry_width = 24 if is_story else 30
    meta_top = 138 if is_story else 116
    entry_top = 286 if is_story else 250
    footer_y = height - (120 if is_story else 88)

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; width: {width}px; height: {height}px; overflow: hidden; }}
  body {{
    background: {background};
    color: {ink};
    font-family: Nunito, Avenir, Helvetica, Arial, sans-serif;
  }}
  .canvas {{
    width: {width}px;
    height: {height}px;
    position: relative;
    overflow: hidden;
    background:
      radial-gradient(circle at 18% 12%, {accent}1c, transparent 34%),
      radial-gradient(circle at 82% 84%, {accent}16, transparent 30%),
      {background};
  }}
  .grain {{
    position: absolute;
    inset: 0;
    opacity: 0.048;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 170px 170px;
  }}
  .studio-note {{
    position: absolute;
    top: 86px;
    left: 92px;
    color: {muted};
    font-size: 22px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }}
  .texture {{
    position: absolute;
    top: 86px;
    right: 92px;
    color: {muted};
    font-size: 17px;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    opacity: 0.68;
  }}
  .phone {{
    position: absolute;
    left: 50%;
    top: {phone_top}px;
    width: {phone_width}px;
    height: {phone_height}px;
    transform: translateX(-50%);
    border-radius: 42px;
    background: color-mix(in srgb, {background} 88%, white);
    border: 1px solid color-mix(in srgb, {accent} 24%, transparent);
    box-shadow: 0 38px 100px rgba(28, 26, 23, 0.11);
    overflow: hidden;
  }}
  .phone::before {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(145deg, rgba(255,255,255,0.32), transparent 38%);
    pointer-events: none;
  }}
  .topbar {{
    position: absolute;
    top: 42px;
    left: 54px;
    right: 54px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: {muted};
    font-size: 21px;
    letter-spacing: 0.07em;
  }}
  .brand {{
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    color: {ink};
    font-size: 34px;
    letter-spacing: 0.05em;
  }}
  .entry-meta {{
    position: absolute;
    left: 64px;
    right: 64px;
    top: {meta_top}px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .dot {{
    width: 14px;
    height: 14px;
    border-radius: 999px;
    background: {accent};
    box-shadow: 0 0 0 8px {accent}18;
  }}
  .date {{
    color: {muted};
    font-size: 22px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}
  .sense {{
    margin-left: auto;
    color: {accent};
    border: 1px solid {accent}38;
    border-radius: 999px;
    padding: 7px 16px;
    font-size: 17px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}
  .entry {{
    position: absolute;
    left: 64px;
    right: 64px;
    top: {entry_top}px;
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    color: {ink};
    font-size: {entry_size}px;
    line-height: 1.2;
    letter-spacing: -0.02em;
  }}
  .save-row {{
    position: absolute;
    left: 64px;
    right: 64px;
    bottom: 58px;
    border-top: 1px solid {accent}38;
    padding-top: 28px;
    display: flex;
    justify-content: space-between;
    color: {muted};
    font-size: 20px;
  }}
  .prompt {{
    position: absolute;
    left: 92px;
    right: 92px;
    top: {phone_top + phone_height + (58 if is_story else 42)}px;
    text-align: center;
    color: {muted};
    font-size: {28 if is_story else 23}px;
    line-height: 1.45;
  }}
  .footer {{
    position: absolute;
    left: 92px;
    right: 92px;
    bottom: {footer_y}px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: {muted};
    font-size: 24px;
  }}
  .footer .word {{
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    color: {ink};
    font-size: 31px;
  }}
  .eye {{
    width: 82px;
    height: 52px;
    opacity: 0.42;
  }}
</style>
</head>
<body>
  <main class="canvas">
    <div class="grain"></div>
    <div class="studio-note">a real noticing</div>
    <div class="texture">{html.escape(texture)}</div>
    <section class="phone">
      <div class="topbar"><span class="brand">nazar</span><span>saved</span></div>
      <div class="entry-meta">
        <span class="dot"></span>
        <span class="date">{html.escape(label)}</span>
        <span class="sense">{html.escape(sense)}</span>
      </div>
      <div class="entry">“{wrap(entry, entry_width)}”</div>
      <div class="save-row"><span>kept privately</span><span>local-first</span></div>
    </section>
    <p class="prompt">for the small things that would sound too small anywhere else</p>
    <div class="footer">
      <span class="word">nazar</span>
      <svg class="eye" viewBox="0 0 90 56" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="45" cy="28" rx="36" ry="18" stroke="{accent}" stroke-width="2"/>
        <circle cx="45" cy="28" r="8" stroke="{accent}" stroke-width="2"/>
        <circle cx="45" cy="28" r="3" fill="{accent}"/>
      </svg>
    </div>
  </main>
</body>
</html>"""


def render(page_html: str, output_path: Path, width: int, height: int, temp_dir: Path) -> None:
    source = temp_dir / f"{output_path.stem}.html"
    profile = temp_dir / f"{output_path.stem}-chrome"
    source.write_text(page_html)
    output_path.unlink(missing_ok=True)
    proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-extensions",
            "--hide-scrollbars",
            f"--user-data-dir={profile}",
            f"--window-size={width},{height}",
            f"--screenshot={output_path}",
            source.resolve().as_uri(),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + 20
    try:
        while time.time() < deadline:
            if output_path.exists() and output_path.stat().st_size > 0:
                return
            if proc.poll() is not None:
                break
            time.sleep(0.1)
        if output_path.exists() and output_path.stat().st_size > 0:
            return
        raise RuntimeError(f"Chrome did not render {output_path}")
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()


def clear_old_assets() -> None:
    for folder in (POSTS, STORIES):
        folder.mkdir(parents=True, exist_ok=True)
        for path in folder.glob("*.png"):
            path.unlink()


def main() -> None:
    clear_old_assets()
    data = json.loads(SOURCE.read_text())
    items = data["items"]
    rows = []

    with tempfile.TemporaryDirectory(prefix="nazar-render-") as temp:
        temp_dir = Path(temp)
        for item in items:
            day = int(item["campaignDay"])
            stem = f"nazar-entry-{day:03d}"
            post_path = POSTS / f"{stem}-post.png"
            story_path = STORIES / f"{stem}-story.png"
            render(page(item, "post"), post_path, 1080, 1350, temp_dir)
            render(page(item, "story"), story_path, 1080, 1920, temp_dir)
            rows.append(
                {
                    "campaign_day": day,
                    "date": item["date"],
                    "label": item["label"],
                    "sense": item.get("sense", ""),
                    "entry": item["entry"],
                    "caption": item["caption"],
                    "post_file": f"posts/{post_path.name}",
                    "story_file": f"stories/{story_path.name}",
                }
            )

    with CAPTIONS.open("w", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "campaign_day",
                "date",
                "label",
                "sense",
                "entry",
                "caption",
                "post_file",
                "story_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"generated {len(items)} entry posts in {POSTS}")
    print(f"generated {len(items)} entry stories in {STORIES}")
    print(f"wrote {CAPTIONS}")


if __name__ == "__main__":
    main()

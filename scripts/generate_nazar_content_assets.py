#!/usr/bin/env python3
"""Generate 30 Nazar Instagram post/story assets starting on June 10."""

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
SOURCE = ROOT / "artifacts/nazar/public/content/nazar-content-engine.json"
POSTS = ROOT / "content/posts"
STORIES = ROOT / "content/stories"
CAPTIONS = ROOT / "content/captions.csv"
CHROME = "/usr/local/bin/google-chrome"
START_MONTH = 6
START_DAY = 10
ASSET_COUNT = 30

SENSE_COLORS = {
    "sight": "#085041",
    "sound": "#534AB7",
    "smell": "#BA7517",
    "taste": "#D4537E",
    "touch": "#D85A30",
    "feeling": "#1D9E75",
}


def card_line(item: dict) -> str:
    blocks = item.get("shareCardDesign", {}).get("copyBlocks", [])
    for block in blocks:
        if block.get("role") == "main" and block.get("text"):
            return block["text"]

    prompt = item["noticingPrompt"]
    for prefix in [
        "Notice ",
        "Give attention to ",
        "Stay with ",
        "Let yourself find ",
        "Look for ",
        "Listen for ",
        "Receive ",
        "Name ",
        "Follow ",
        "Hold ",
    ]:
        if prompt.startswith(prefix):
            prompt = prompt[len(prefix) :]
            break
    for marker in [
        " through ",
        " by listening first",
        " as taste",
        " without ",
        " with ",
        ". Stay",
    ]:
        if marker in prompt:
            prompt = prompt.split(marker)[0]
            break
    return prompt.strip().strip(".") or item["noticingPrompt"]


def wrap(text: str, width: int) -> str:
    lines = textwrap.wrap(text, width=width, break_long_words=False)
    return "<br>".join(html.escape(line) for line in lines)


def page(item: dict, kind: str) -> str:
    is_story = kind == "story"
    width, height = (1080, 1920) if is_story else (1080, 1350)
    design = item.get("shareCardDesign", {})
    palette = design.get("palette", {})
    background = palette.get("background", "#F7F4EF")
    ink = palette.get("text", "#1C1A17")
    muted = palette.get("muted", "#B0A89E")
    accent = palette.get("accent") or SENSE_COLORS.get(item.get("sense"), "#085041")
    title_size = 96 if is_story else 82
    prompt_size = 32 if is_story else 29
    eyebrow_top = 620 if is_story else 420
    footer_top = height - (150 if is_story else 112)
    title_width = 20 if is_story else 24
    prompt_width = 52 if is_story else 58
    eye_top = 166 if is_story else 118
    eye_width = 314 if is_story else 250
    title = card_line(item)
    prompt = item["noticingPrompt"]
    day = f"{item['monthName'].lower()} {item['dayOfMonth']}"
    texture = design.get("texture", "subtle paper grain")

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
  .card {{
    width: {width}px;
    height: {height}px;
    position: relative;
    overflow: hidden;
    background:
      radial-gradient(circle at 74% 14%, {accent}24, transparent 34%),
      radial-gradient(circle at 20% 84%, {accent}14, transparent 30%),
      {background};
  }}
  .grain {{
    position: absolute;
    inset: 0;
    opacity: 0.045;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 180px 180px;
  }}
  .eye {{
    position: absolute;
    top: {eye_top}px;
    left: 50%;
    width: {eye_width}px;
    height: {int(eye_width * 0.58)}px;
    transform: translateX(-50%);
    opacity: 0.18;
  }}
  .copy {{
    position: absolute;
    left: 108px;
    right: 108px;
    top: {eyebrow_top}px;
  }}
  .eyebrow {{
    color: {muted};
    font-size: 30px;
    letter-spacing: 8px;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 54px;
  }}
  .title {{
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-size: {title_size}px;
    line-height: 0.98;
    letter-spacing: -1.4px;
    color: {ink};
  }}
  .rule {{
    position: absolute;
    left: 108px;
    right: 108px;
    top: {footer_top - 56}px;
    border-top: 2px solid {accent};
    opacity: 0.4;
  }}
  .prompt {{
    position: absolute;
    left: 108px;
    right: 108px;
    top: {footer_top}px;
    color: {ink};
    font-size: {prompt_size}px;
    line-height: 1.45;
    font-weight: 300;
  }}
  .footer {{
    position: absolute;
    left: 108px;
    right: 108px;
    bottom: 58px;
    display: flex;
    justify-content: space-between;
    color: {muted};
    font-size: 25px;
    letter-spacing: 0.02em;
  }}
  .brand {{ font-family: Georgia, 'Times New Roman', serif; font-style: italic; }}
  .texture {{
    position: absolute;
    right: 92px;
    top: 82px;
    color: {muted};
    font-size: 18px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.58;
  }}
</style>
</head>
<body>
  <main class="card">
    <div class="grain"></div>
    <div class="texture">{html.escape(texture)}</div>
    <svg class="eye" viewBox="0 0 360 220" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="180" cy="110" rx="150" ry="70" stroke="{accent}" stroke-width="5"/>
      <circle cx="180" cy="110" r="34" stroke="{accent}" stroke-width="5"/>
      <circle cx="180" cy="110" r="13" fill="{accent}"/>
    </svg>
    <section class="copy">
      <div class="eyebrow">today i noticed</div>
      <div class="title">{wrap(title, title_width)}</div>
    </section>
    <div class="rule"></div>
    <div class="prompt">{wrap(prompt, prompt_width)}</div>
    <div class="footer"><span class="brand">nazar</span><span>{html.escape(day)}</span></div>
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


def main() -> None:
    POSTS.mkdir(parents=True, exist_ok=True)
    STORIES.mkdir(parents=True, exist_ok=True)
    engine = json.loads(SOURCE.read_text())
    all_items = engine["items"]
    start_index = next(
        index
        for index, item in enumerate(all_items)
        if item["month"] == START_MONTH and item["dayOfMonth"] == START_DAY
    )
    items = all_items[start_index : start_index + ASSET_COUNT]
    rows = []

    with tempfile.TemporaryDirectory(prefix="nazar-render-") as temp:
        temp_dir = Path(temp)
        for index, item in enumerate(items, start=1):
            stem = f"nazar-day-{index:03d}"
            post_path = POSTS / f"{stem}-post.png"
            story_path = STORIES / f"{stem}-story.png"
            render(page(item, "post"), post_path, 1080, 1350, temp_dir)
            render(page(item, "story"), story_path, 1080, 1920, temp_dir)
            rows.append(
                {
                    "campaign_day": index,
                    "source_day_of_year": int(item["dayOfYear"]),
                    "date": item["date"],
                    "label": f"{item['monthName']} {item['dayOfMonth']}",
                    "sense": item.get("sense", ""),
                    "prompt": item["noticingPrompt"],
                    "caption": item["instagramCaption"],
                    "post_file": f"posts/{post_path.name}",
                    "story_file": f"stories/{story_path.name}",
                }
            )

    with CAPTIONS.open("w", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "campaign_day",
                "source_day_of_year",
                "date",
                "label",
                "sense",
                "prompt",
                "caption",
                "post_file",
                "story_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"generated {len(items)} posts in {POSTS}")
    print(f"generated {len(items)} stories in {STORIES}")
    print(f"wrote {CAPTIONS}")


if __name__ == "__main__":
    main()

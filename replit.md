# Nazar — Daily Noticing Journal

A meditative single-page web app for noticing and recording small beautiful things each day.

## Run & Operate

- App is at `artifacts/nazar/index.html`, served via Vite
- No build step needed — pure HTML/CSS/JS single file
- Workflow: `artifacts/nazar: web` (auto-started)

## Stack

- Pure HTML + CSS + JS, zero runtime dependencies
- Google Fonts: Nunito (UI) + Lora (body/entries)
- Web Audio API for ambient sound + save bell
- `localStorage` only — no server, no account

## Where things live

- `artifacts/nazar/index.html` — entire app (~2100 lines)
- CSS vars: `--cream`, `--ink`, `--ink2`, `--ink3` (light + dark overrides in `@media (prefers-color-scheme: dark)`)
- SENSES array: sight / sound / smell / taste / feeling (each with color)
- 48 "others noticed" rotating observations

## Architecture decisions

- Single-file design intentional — no bundler complexity, instant load, easy share
- localStorage key: `nazar_entries` (array of `{id, text, sense, date}`)
- Audio: `AudioContext` unlocked on first touch/click for iOS Safari compatibility
- Dark mode via CSS custom property overrides in `@media (prefers-color-scheme: dark)` — no JS toggle
- Intersection Observer drives staggered journal entry reveal (no scroll event listeners)

## Product

- Home screen: eye illustration, rotating "others noticed" observations, ambient sound toggle
- Notice screen: date, sense selector, textarea, 1-minute optional timer with depleting ring
- Timer: cycling sense words (look/listen/feel/breathe/notice), bell on complete, haptic feedback
- Settle overlay: 3.2s italic entry display before journaling to journal
- Journal screen: chronological entries with staggered fade-in reveal
- Archive screen: filter by sense (sight / smell / feeling)
- Year overlay: shown every 10 entries as a quiet milestone

## User preferences

- No streaks, no gamification, no journaling prompts
- No server storage — localStorage only
- Everyday beauty, not abstract poetry ("Life integrates art")
- Goal: award-winning, quiet, intimate feel

## Gotchas

- Eye SVG ellipses/circles use hardcoded stroke/fill — dark mode overrides via `.eye-svg ellipse`, `.eye-svg circle:nth-child(n)` selectors
- `ringSave()` and `timerComplete()` both call `haptic()` — navigator.vibrate is mobile-only (silent on desktop)
- Swipe navigation only works between `['notice', 'journal', 'archive']` screens, not from home/timer
- Custom cursor only activates on `(pointer: fine)` devices; hidden on touch via `(pointer: coarse)`

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details

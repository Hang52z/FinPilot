# 0002 — Web app from the same Expo codebase

Date: 2026-11-25 · Status: Accepted

## Decision

Build the web app from `apps/mobile` with Expo's web target and host the static output on
Cloudflare Pages. The API stays on its own subdomain (`finpilotapi.<domain>`); the backend allows the
web origin through `CORS_ORIGINS`.

## Why

- One codebase: every screen, string and design token ships to iOS, Android and web at once.
  A separate web app (e.g. Next.js) would duplicate UI and logic.
- Single-page output (`web.output: "single"`): no server needed, and Cloudflare Pages serves
  `index.html` for every path, so deep links work.
- Separate API subdomain: phones and web use the same API URL. A same-origin proxy on Cloudflare
  would avoid CORS but adds routing rules to maintain.

## Effects

- UX: same interface everywhere; the browser tab follows the chosen language (`<html lang>`).
- DX: one `npm run check` covers all three targets, including the web build; `make web` for local work.
- AX: one place to change UI; the rule "works on iOS, Android and web" is in AGENTS.md.

## Trade-offs

- Web uses React Native Web, which looks native-like rather than like a typical website. Accepted:
  it matches the Apple Notes style and avoids a second UI.

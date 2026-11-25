# 0001 — Phase 0 foundation choices

Date: 2026-11-25 · Status: Accepted

## Docker-first

Compose is the single way to run and check the backend, locally and in CI (`make check` runs the
same commands CI runs). The mobile app runs on the host because simulators and devices cannot run
inside Docker; its checks also run in a `node:22` container for parity.

- UX: no effect. DX: one command, no local Python or Postgres. AX: agents run the same checks CI does.

## uv for Python, npm for mobile

uv gives a lockfile and fast, reproducible installs. npm is what Expo ships with; no extra tool.

## jest-expo instead of Vitest for mobile tests

PLAN.md lists Vitest. React Native code does not run reliably under Vitest; `jest-expo` is the
Expo-supported runner and works with React Native Testing Library and Expo Router's test utilities.
Backend tests use pytest as planned. Vitest can still be used for any future pure-TypeScript package.

- DX/AX: tests use the toolchain the platform documents, so fewer surprises.

## Empty baseline migration

`0001_baseline` creates nothing. It satisfies "initial migration" while keeping the rule that tables
are created only by the phase that needs them.

## Minimal screens

All four tabs render only their title. Home shows nothing while the server is healthy; when the API
or database is unreachable it shows one error row with Retry. This meets "app connects to FastAPI"
without placeholder data or status chrome.

## JS tabs, not native tabs

`expo-router/js-tabs` gives headers (title + Settings button) without nesting a stack in every tab.
Native tabs can replace it later without changing routes.

## English default, Chinese switchable

i18next with two locale files. English is always the default (no device detection yet). The switch
lives in Settings, reached from the header, per PLAN.md §4.1. A test keeps both locales' keys identical.
The backend stays language-neutral.

- UX: one tap to switch. DX: typed keys (`t('tabs.home')` is checked by TypeScript). AX: one place per language.

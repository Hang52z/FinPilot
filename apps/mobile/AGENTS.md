# Mobile — agent notes

Read the root [AGENTS.md](../../AGENTS.md) first. This file adds Expo specifics.

- Expo SDK 58. APIs change between SDKs — check the versioned docs at
  `https://docs.expo.dev/versions/v58.0.0/` (or the package's `.d.ts`) instead of relying on memory.
- Add packages with `npx expo install <pkg>`, never plain `npm install`, so versions match the SDK.
- Routes live in `app/`. Keep non-route code (components, hooks, services) outside it.
- Import `Link`, `Stack`, `router` from `expo-router`; tabs from `expo-router/js-tabs`.
- React Native Testing Library v14: `render`, `rerender`, `unmount` and `userEvent` calls are async — `await` them.
- `ios/` and `android/` are generated. Never create or edit them by hand; configure via `app.json`.
- Before finishing: `npm run check` (lint, typecheck, tests).

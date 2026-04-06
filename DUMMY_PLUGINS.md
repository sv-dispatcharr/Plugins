# Dummy Test Plugins

This branch contains 15 dummy plugins for testing the Dispatcharr plugin hub, manifest generation, and plugin UI. None of them do anything beyond logging at INFO level.

---

## Normal Plugins

### `hello-logger` · nachtfalter · MIT
The simplest possible plugin. One action, no fields, no deps. Baseline smoke test for install, enable, and action execution.

### `channel-counter` · prixdevs · Apache-2.0
Queries `Channel.objects.count()` and returns the result. Tests that installed plugins can reach internal Django models.

### `settings-tester` · kelvinmoss · BSD-2-Clause
Exercises every supported field type: `string`, `number`, `boolean`, `select`, and `text` (textarea). Useful for testing the settings form renderer end-to-end.

### `epg-reporter` · solarflux42 · GPL-3.0-only
Queries `EPGSource.objects.count()`. Pairs with `channel-counter` to verify access to different app models.

### `uptime-greeter` · wrenwick · ISC
Has a single configurable `string` field (`greeting`) and logs it with the current UTC timestamp. Tests that settings values are correctly passed through `context["settings"]`.

### `m3u-lister` · tobiasfendt · MPL-2.0
Returns a list of all M3U account names from the DB. Tests list responses and multi-model access.

### `websocket-pinger` · radarlabs · BSD-3-Clause
Calls `send_websocket_update` and logs the result. Tests that installed plugins can reach `core.utils`.

### `multi-action-demo` · devklara · Unlicense
Three distinct action buttons (`action_one`, `action_two`, `action_three`). Tests that the UI correctly renders and dispatches multiple actions on the same card.

### `password-field-demo` · quentinash · LGPL-2.1-only
Has a `string` field with `"input_type": "password"`. The action logs whether a key is set (never the value). Tests masked input rendering and safe settings handling.

### `confirm-action-demo` · irinakorb · MIT
Has a safe action (no prompt) and a risky action with a `confirm` object (`required`, `title`, `message`). Tests the confirmation modal flow end-to-end.

### `info-field-demo` · maddoxwren · Apache-2.0
Uses `info`-type fields as section headers and inline notes alongside regular fields. Tests display-only field rendering.

---

## Nuanced Plugins

### `legacy-notifier` · hartleydev · BSD-3-Clause — **deprecated**
`plugin.json` sets `"deprecated": true`. Verifies that the `deprecated` flag is included in the root manifest and surfaced correctly in the plugin hub UI.

### `internal-debug-tool` · nnvoss · ISC — **unlisted**
`plugin.json` sets `"unlisted": true`. The per-plugin `manifest.json` is still generated and the plugin README is still produced, but the plugin does **not** appear in the root `manifest.json` or the releases README. Tests the unlisted path through `generate-manifest.sh`.

### `version-gated-plugin` · cosmicreed · MPL-2.0 — **version range**
Sets both `"min_dispatcharr_version": "v0.20.0"` and `"max_dispatcharr_version": "v0.21.99"`. Tests version compatibility gating in the plugin hub install flow.

### `well-linked-plugin` · jasperveld · EUPL-1.2 — **full metadata**
Has `repo_url`, `discord_thread` (a `discord.com/channels/` URL to exercise the `discord://` protocol link path), and a non-MIT license (`EUPL-1.2`). Tests that all optional metadata links render correctly on the plugin card and detail modal.

### `retired-internal-tool` · pelikandev · GPL-3.0-only — **deprecated + unlisted**
Sets both `"deprecated": true` and `"unlisted": true`. Should not appear in the root manifest or releases README. The per-plugin manifest and README are still generated. Tests the combination of both flags together.

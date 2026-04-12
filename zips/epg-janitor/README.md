[Back to All Plugins](../../README.md)

# EPG Janitor

**Version:** `1.26.1021352` | **Author:** PiratesIRC | **Last Updated:** Apr 12 2026, 19:22 UTC

Scans for channels with EPG assignments but no program data. Auto-matches EPG to channels using intelligent fuzzy matching with aliases, removes EPG from hidden channels, and manages EPG assignments.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](https://spdx.org/licenses/MIT.html) [![Discord](https://img.shields.io/badge/Discord-Discussion-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com/channels/1340492560220684331/1420051973994053848) [![Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/PiratesIRC/Dispatcharr-EPG-Janitor-Plugin)

![Dispatcharr min](https://img.shields.io/badge/Dispatcharr_min-v0.20.0-brightgreen?style=flat-square)

## Downloads

### Latest Release

- **Download:** [`epg-janitor-latest.zip`](https://github.com/sv-dispatcharr/Plugins/raw/releases/zips/epg-janitor/epg-janitor-latest.zip)
- **Built:** Apr 12 2026, 20:17 UTC
- **Source Commit:** [`2cf371a`](https://github.com/sv-dispatcharr/Plugins/commit/2cf371ad80c2219d832938067564d40b038ccd26)

**Checksums:**
```
MD5:    27ba964b3c6fa8c7aacd900782bdaa45
SHA256: cc61e3582ffb0480b9524e4f14c10d5f60f617591e631a11892be17e6e7dec1c
```

### All Versions

| Version | Download | Built | Commit | MD5 | SHA256 |
|---------|----------|-------|--------|-----|--------|
| `1.26.1021352` | [Download](https://github.com/sv-dispatcharr/Plugins/raw/releases/zips/epg-janitor/epg-janitor-1.26.1021352.zip) | Apr 12 2026, 20:17 UTC | [`2cf371a`](https://github.com/sv-dispatcharr/Plugins/commit/2cf371ad80c2219d832938067564d40b038ccd26) | 27ba964b3c6fa8c7aacd900782bdaa45 | cc61e3582ffb0480b9524e4f14c10d5f60f617591e631a11892be17e6e7dec1c |

---

**Maintainers:** PiratesIRC | **Source:** [Browse Plugin](https://github.com/sv-dispatcharr/Plugins/tree/main/plugins/epg-janitor)

**Metadata:** [View full manifest](./manifest.json)

---

## Plugin README

# EPG Janitor

Keep your Electronic Program Guide clean, accurate, and complete. EPG Janitor operates on channels that already exist in Dispatcharr — it finds broken EPG assignments (no program data), intelligently matches EPGs to channels using callsign/location/network scoring plus a fuzzy pipeline with built-in aliases, and provides bulk cleanup tools for removing EPG from hidden channels or by REGEX.

**Source repo:** https://github.com/PiratesIRC/Dispatcharr-EPG-Janitor-Plugin
**Discord thread:** https://discord.com/channels/1340492560220684331/1420051973994053848

## Requires

Dispatcharr v0.20.0 or newer. Python 3.13+ (bundled). No external dependencies.

## Key features

- **Auto-Match EPG** — weighted structural scoring (callsign 50 / state 30 / city 20 / network 10) + Lineuparr-style 4-stage fuzzy pipeline (alias → exact → substring → token-sort), takes the higher score. Identical-name matches score 100.
- **Scan & Heal** — find channels whose current EPG has no program data and walk ranked candidates for a working replacement (respects fallback source allowlist).
- **~200 built-in aliases** (FS1/FS2, CSPAN variants, rebrands like EPIX→MGM+, MSNBC→MS NOW, getTV→GREATTV, DIY→Magnolia, Hallmark Movies & Mysteries→Hallmark Mystery, Justice Network→True Crime Network). User-extendable via a JSON `custom_aliases` setting.
- **Regional differentiation** (East/West/Pacific, Pacific ≡ West) — lineup channels with regional markers only match compatible EPG feeds, even when `ignore_regional_tags=true`.
- **Per-category normalization toggles** — quality (`[HD]`, `[4K]`), regional (East/West/Pacific), geographic (`US:`, `[CA]`), misc (`(A)`, `(CX)`) stripped independently.
- **Performance** — pre-normalization cache + per-EPG attribute cache. ~7–8 min for a 21,480-EPG × 2,950-channel run.
- **Bulk management** — remove EPG by REGEX, from hidden channels, or from entire groups. Tag channels with missing program data via configurable suffix.
- **CSV exports** — every dry-run and apply exports results with confidence scores, match method, and reasoning.

## Settings

Organized into sections via UI dividers: Scope, Auto-Match, Scan & Heal, Cleanup & Maintenance, Normalization Toggles, Custom Aliases. Dynamic per-country channel-database toggles (US, UK, CA, DE, ES, FR, IN, MX, NL, AU, BR) auto-generated based on shipped `*_channels.json` files.

## Actions

14 color-coded action buttons grouped by destructiveness (blue outlines for info, cyan for dry-runs, green-filled for apply-style, orange/red-filled for destructive) with confirmation dialogs on anything that mutates channel state. Emoji labels.

## How it differs from other matching plugins

- **Not a channel creator.** EPG Janitor does not create channels or scan M3U sources — it works on channels you already have in Dispatcharr. For provider-lineup-driven channel creation see [Lineuparr](https://github.com/PiratesIRC/Dispatcharr-Lineuparr-Plugin).
- **EPG-first matching.** The weighted pipeline is tuned for matching EPG entries (which often carry callsigns + geographic context for US broadcast) rather than IPTV stream names.
- **Heal semantics.** First-class support for replacing broken EPG assignments with working ones — walks ranked candidates and validates program-data availability before applying.

## Install

Install from the Dispatcharr Plugin Hub (once available) or download the latest release from the source repo and import via **Plugins → Import Plugin** in the Dispatcharr UI.

## License

MIT © 2026 PiratesIRC

---

*All product names, trademarks, and registered trademarks mentioned in this project are the property of their respective owners. Channel alias data is community-compiled from publicly available information and is not affiliated with or endorsed by any broadcaster.*

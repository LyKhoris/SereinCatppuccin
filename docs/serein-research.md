# Serein research: Catppuccin Mocha with Blue

Research date: **2026-11-14**. Scope: understand Serein and its extension APIs, then implement **one Mocha theme with Blue (`#89b4fa`)**, using **only exact official Mocha palette colors** in authored values. After research, the user accepted host-controlled rendering exceptions and implementation proceeded. The package is `../catppuccin-mocha-blue.serein-extension`; validation details are in `../README.md`. Frontend-design guidance is limited to color selection, not layout, typography, or geometry redesign.

## Conclusions

- **The client is [`ViceVerse-cz/Serein`](https://github.com/ViceVerse-cz/Serein)**, an unofficial native Discord desktop client written in Rust with egui/eframe and wgpu—not a Discord web-client modification. Target platforms are Linux, macOS, and Windows. [S1][S2]
- **Use a declarative `.serein-extension` JSON theme**, containing a v1 manifest and named palette values. No Wasm, JavaScript, CSS, Node tooling, or plugin permissions are needed for this port. [S3][S4]
- **BetterDiscord CSS is not supported by this theme API.** The official specification explicitly prohibits CSS/script injection; the source accepts a bounded declarative schema and rejects unknown fields. Existing Catppuccin Discord `.theme.css` files are visual references, not installable Serein themes. [S3][S4][C4]
- Serein exposes an **`accent_text` token**, so use Mocha Base on Blue-filled buttons. Mocha Text on Blue has poor contrast. [S3][S6][C1][C2]
- Pin and test an exact Serein build. Current source, preview-labelled docs, the older wiki, and released nightlies are not interchangeable. An important source/docs disagreement about accent precedence is recorded below. [S3][S6][S10]
- **Strict renderer-wide palette purity is not achievable through the inspected theme API alone.** Upstream code derives button-state/selection colors and hard-codes white on some controls. The user accepted these host-controlled exceptions; every authored theme value still uses an exact opaque Mocha entry. [S6]

## Evidence and version boundaries

**[Docs]** means an official project document; **[Source]** means behavior inspected in its implementation; **[Recommendation]** means a proposed choice for this port, not an upstream requirement.

Serein source and repository documentation below are pinned to **`bedb57c0c8def62e736e8a4f03e0a5d248b22126`**, the `main` commit returned by GitHub during research, committed **2026-11-14 00:27 UTC**. This is a source baseline, not a claim that a user's installed binary contains it. [S0]

The releases API's first entry at research time was **`v1.0.0-nightly.20261113.90`**, published 2026-11-13 and marked prerelease. `/releases/latest` returned 404; use the releases list rather than assuming a stable release exists. Its assets include Linux x64 formats, Ubuntu ARM64 `.deb`, macOS ARM64, and Windows x64/ARM64. Architecture availability is not equivalent to verified runtime support. [S2][S10]

The official wiki banner points to older source **`7ddd47cade4ca14bd964abc70f7391f3919f441f`** and calls itself preview SDK PR #641. Current repository documents still label some APIs preview/not yet released: `style.icon_size` and `external_navigation` (PR #937), scheduled appearance ticks (PR #286), and certain host actions (PR #411). Prefer the pinned repository schema and the actual target binary over examples copied blindly from the wiki. ABI `api_version: 1` does **not** promise every later-added field is supported by older hosts. [S3][S5][S9]

## 1. Identity, architecture, platforms, and official documentation

**[Docs]** Serein connects directly to Discord gateway and REST endpoints for existing accounts. Its README explicitly says it is unofficial, not endorsed by Discord, and warns of Terms-of-Service/account-termination risk. Theme development can start with synthetic demo data without an account. [S1]

**[Docs + Source]** The main UI is immediate-mode native Rust: egui/eframe with wgpu rendering. The Cargo workspace separates desktop lifecycle, UI, client state, protocol/gateway/API, SQLite storage, OS integration, and extensions. Tokio supports asynchronous work; `wry` provides a temporary native authentication webview, not a browser-based application UI. Plugins execute through the `wasmi` Wasm interpreter. [S1][S7][S8]

**[Docs]** Platform support targets Windows/macOS/Linux, with local build evidence for macOS ARM64, Windows x64, and Linux x64. Windows ARM64 and Ubuntu ARM64 are workflow targets but the platform guide says build/runtime validation remains pending. Native visual checks are stronger on macOS than on other platforms; minimum OS versions and accessibility/IME support are not comprehensively certified. [S2]

Official reading order:

| Purpose | Primary source |
| --- | --- |
| Client overview, installation, source-build prerequisites | [README][S1] |
| Platforms and validation caveats | [Platform support][S2] |
| Native theme package, tokens, editor, backgrounds, limits | [Theme API][S3] |
| Host contract, permissions, installation, lifecycle, sandbox | [Community extensions][S5] |
| First plugin, manifest, ABI, building and testing | [Extension authoring guide][S9] |
| Navigation to SDK data/actions/troubleshooting documents | [SDK overview][S11] |
| Official theme/plugin examples and catalog publishing | [Extensions directory README][S12] |
| Renderer, design roles, built-in presets and typography | [Design guide][S13] and [implementation][S6] |
| Creator-oriented wiki, explicitly older preview revision | [Wiki home][S14] and [Creating a Theme][S15] |

The repository links a GitHub Pages endpoint for package repositories/Flatpak, e.g. `https://viceverse-cz.github.io/Serein/`; the source repository and its docs/wiki are the verified authoring authorities here. The separate historical `Serein-extensions`/`Serein-themes` repositories are not the canonical current catalog: packages now live in `Serein/extensions/`. [S1][S12]

## 2. Plugins: what they are and when one is unnecessary

### Manifest and package

**[Docs + Source]** A plugin package is one JSON file with `manifest` and `wasm` (a JSON byte array). Its manifest has `api_version`, `id`, `name`, `version`, `author`, `license`, `source`, `kind: "plugin"`, `capabilities`, and `actions`. Themes use the same identity metadata but `kind: "theme"`, no actions/capabilities, a `theme` object, and no Wasm. [S4][S9]

- API version must be `1`; plugin IDs use lowercase ASCII letters/digits/hyphens, begin with a letter/digit, and are at most 64 bytes; Windows device names are reserved. Imported theme IDs are ASCII-lowercased before validation. [S4][S9]
- Name/version/author/license must be nonempty, no control characters, at most 128 UTF-8 bytes. Semantic versioning is not enforced. Public source links must be credential-free HTTPS; a local theme alone may use an empty source. Catalog publishing still requires proper source metadata. [S3][S4][S9]
- Plugins need 1–16 unique actions; themes need zero. `capabilities` and `actions` default to empty if omitted. Unknown fields and unsupported enum values are rejected. [S4][S9]

### APIs, permission model, and lifecycle

**[Docs + Source]** A plugin is a JSON-in/JSON-out function. Each invocation receives a **fresh Wasm instance**, destroyed afterward; globals do not provide persistent state. No WASI or host imports are permitted. It cannot directly read credentials, filesystem, network, Discord APIs, arbitrary egui objects, or render callbacks. The host supplies separately granted, bounded snapshots of already-loaded app data. Persistent settings use the separately granted `storage` output. [S5][S8][S9]

Relevant action surfaces are `panel`, `message`, `composer`, `activation`, `message_event`, `app_event`, and preview `tick`; context-menu actions also exist for user/channel/server/role targets. Activation runs on enable/account load. At most one action of each automatic surface is allowed. Message/app events are best effort, bounded, and not a replay log. Foreground host-effect proposals need explicit native **Apply** confirmation; background events cannot send messages or open arbitrary panels. [S4][S5][S9]

An `appearance`-granted plugin may return the same declarative theme shape as an overlay, optionally restoring choices via `storage` during activation. A new appearance object replaces that plugin's prior overlay; omission leaves it unchanged; `{}` clears it. Enabled appearance plugins overlay the selected theme in ascending plugin-ID order, with the last explicit value winning. Disabling removes its overlay; emergency reset clears community theme/appearance overrides. **This machinery is unnecessary for one fixed Mocha/Blue palette.** [S5]

Normal plugins' grants/data are account scoped. Logout invalidates results and clears that account's extension data. Themes are device scoped. Disable removes the installed package and extension data; it does not delete the author's repository or imported original. The special pre-login `api_proxy` plugin is device scoped and restricted to REST routing, not a general networking API. [S5]

Sandbox limits include 4 MiB Wasm, 16 MiB JSON package, 16 MiB linear memory, 10 million fuel, 256 KiB serialized input/output each, and 1 MiB stored data (also subject to smaller invocation limits). Execution happens on an on-demand worker, not rendering/audio callbacks. [S5][S8]

### Build, test, package, install

**[Docs]** Rust authors use the in-repository `serein-extension-sdk`, typed `Invocation`/`AppInvocation`/`Output` wrappers and `export!`; others may implement the same v1 ABI. Required exports are `memory`, `serein_alloc(i32) -> i32`, and `serein_invoke(i32, i32) -> i64`; the returned i64 packs output pointer in the high 32 bits and length in the low 32 bits. JSON wrappers flatten to top-level fields, and Discord IDs are decimal strings. [S8][S9]

Illustrative official plugin workflow, **from a matching Serein source checkout**, not this empty theme repository:

```sh
# From Serein/examples/extensions:
rustup target add wasm32-unknown-unknown
cargo build --locked --release --target wasm32-unknown-unknown -p app-toolbox
python ../../extensions/pack.py app-toolbox/manifest.json target/wasm32-unknown-unknown/release/app_toolbox.wasm packages/app-toolbox.serein-extension

# From Serein root:
cargo run --locked -p extensions --example manifest_check -- examples/extensions/app-toolbox/manifest.json
cargo test --manifest-path examples/extensions/Cargo.toml --workspace --locked
cargo run --locked -p serein --features demo -- --demo
```

Import via **Settings → Extensions**, inspect permissions, then enable. Importing alone does not execute/grant a plugin. After changing source, rebuild/repackage/reimport; source-file edits do not modify installed Wasm. Native `dispatch_typed` tests cover JSON handlers, while `sdk_check` and `legacy_sdk_check` exercise the real offline sandbox; neither is proof of live Discord compatibility or complete install/logout lifecycle testing. [S5][S9]

## 3. Themes: supported format and styling boundaries

### Shape, colors, inheritance

**[Docs + Source]** `.serein-extension` is a JSON package, **not** an archive, CSS file, URL import, or executable. Top-level fields are `manifest`, optional `theme`, optional `wasm`, optional `background_image`, and optional `cover_image`. A theme requires a `theme` object and empty Wasm; its manifest must have no actions/capabilities. `theme` contains optional/defaulted `light`, `dark`, and `style`. Each appearance has a `colors` map, optional two-color `backdrop`, and optional `background` settings. [S3][S4]

All **18** supported color keys:

| Group | Keys |
| --- | --- |
| Surfaces | `base`, `sidebar`, `chat`, `raised`, `hover`, `selected`, `border` |
| Text | `text_strong`, `text`, `muted`, `link` |
| Actions/states | `accent`, `accent_text`, `positive`, `warning`, `danger` |
| Mentions | `mention_bg`, `mention_text` |

Only `#RRGGBB` and `#RRGGBBAA` colors are accepted—not CSS variables, named colors, `rgb()`, arbitrary token names, or nested selectors. Omitted colors inherit the active built-in palette, not an automatic Catppuccin default. Both appearances are optional; omitting `light` does not force dark mode. Omitting `backdrop` gives flat surfaces. Translucent small controls/popouts are composited for readability. [S3][S4][S6]

**[Source/docs discrepancy: accent precedence]** `theme-api.md` and `extensions.md` say the user's custom accent takes precedence. In contrast, current `design.rs::resolved_colors` (lines 823–843) explicitly detects a theme-supplied `accent` and returns it **without** applying `primary_color()`. Thus an explicit theme accent wins at the inspected source baseline. This finding is source-level, not a tested promise about a release binary. Verify the exact installed version with a deliberately different user accent and with appearance plugins enabled/disabled. [S3][S5][S6]

### Native metrics, effects, images, and unsupported features

**[Docs + Source]** Optional `style` applies to both appearances and supports:

| Fields | Bounds; documented defaults |
| --- | --- |
| `body_size`, `button_size`, `small_size`, `monospace_size` | 10–28 logical px; 15/14/12/14 |
| `heading_size` | 12–40; 20 |
| `icon_size` | 16–24; 20; explicitly preview, PR #937 |
| `item_spacing`, `button_padding` | Two integers each, 0–24; `[8,8]` / `[12,6]` |
| `control_height` | 24–56; 32 |
| `widget_radius`, `window_radius`, `menu_radius` | 0–24; 8/12/12 |
| `transparency_blur` | Boolean; permits effects only after device opt-in |
| `transparency`, `blur` | Integer 0–100; otherwise user Appearance settings |

Unknown fields/out-of-range values are rejected. Shared-control metrics do not necessarily change custom-painted widgets or explicit per-widget sizes. A theme cannot rearrange panels, inject CSS/scripts, load fonts, fetch image URLs, or alter message data. A user's separate Appearance font import does not imply theme-packaged font support. [S3][S4][S13]

Window effects require the **Appearance → Transparency & blur** opt-in and a restart when changing that switch. Theme effect percentages can change live during an enabled session. Native blur is compositor-specific; unsupported systems may retain translucency without blur. For predictable Catppuccin colors, begin with effects off and no image/gradient. [S3]

Optional package `background_image` and `cover_image` are **embedded JSON byte arrays** of static PNG/JPEG, up to 2 MiB each. The cover is a shop-card image, independent of the conversation background. Background settings include opacity 0–100, fit `cover`/`contain`, target `chat`/`window`, and section surface coverage for `top_bar`, `server_list`, `channel_list`, `message_list`, `member_list`, and `composer`. Decode bounds include 4,096 px per edge, 4 million pixels and 32 MiB allocation; the entire serialized package remains capped at 16 MiB. No remote image URLs or image file paths are part of a theme. These optional features are unnecessary for the proposed palette. [S3][S4]

**[Source limitation]** `selected` is a native selected/active/hovered-control surface token, **not** independent control of all text-selection behavior. In `design.rs::apply`, native text selection uses `accent.gamma_multiply(0.35)` and an accent stroke; the text cursor uses `text`. The schema has no separate text-selection/cursor token. Consequently Catppuccin's Overlay2-at-20–30% selection recommendation can inform selected surfaces but cannot be imposed on every selection/cursor without upstream changes. [S6][C1]

**[Source limitation: exact-palette constraint]** In `design.rs::sized_button` (lines 2264–2310), Primary uses theme `accent`/`accent_text`, but Danger hard-codes `Color32::WHITE`. Pressed fills are `gamma_multiply(0.82)`, filled-button hover uses `linear_multiply(1.1)`, and disabled fills/text are also attenuated. The shared switch also blends Base/Accent and paints a white knob (lines 2209–2224). These host-derived shades/white are not exact Mocha entries, cannot all be overridden by the 18-token schema, and can create a separate contrast problem on pastel Red. A theme can guarantee only its **authored token values**, not every rendered pixel/state. Do not silently approximate the palette or modify Serein to work around this: present the limitation first if the user's constraint includes host-rendered states. [S6]

### Local iteration, installation, reset, and distribution

**[Docs + Source]** Import the JSON package through **Settings → Themes** and finish the native install/use flow; inactive installed cards expose **Use theme**. Themes are device-wide, persist across restart, and have an eight-installed-theme limit. **Reset / `Ctrl+Shift+F12`** restores built-in appearance while retaining installed themes; **Disable** removes the selected installed package and its local data, not the original exported/imported file. [S3][S5][S16]

The native **Create theme** editor has Basics/Background/Colors/Advanced tabs, temporary app preview, **Save and apply**, and portable **Export**. Imported/catalog themes must be duplicated before editor saves; editor-created local identities can be edited in place. Preview is not a save and does not send messages. [S3]

**No documented filesystem hot-reload contract was found.** Source imports inspect a bounded file, calculate its hash, then copy a validated installed record into the theme store. Editing the exported original is not a documented automatic reload path. Use editor preview/save for live iteration or explicitly reimport an updated package; do not edit internal stored `package.json` records. Source shows local reinstallation can write the same validated theme identity; verify the installed host's UI/replacement behavior. “Live style changes” and preview ticks are not a watched CSS/file workflow. [S3][S16]

For sharing, a downloadable `.serein-extension` plus public source/license is sufficient for manual import. For **official shop inclusion**, add the theme under upstream `extensions/themes/`, retain its stable ID and bump version on changes, optionally add a same-stem PNG preview under `extensions/previews/`, and open a PR. CI runs `python3 catalog.py --validate` and host package checks; after merge the workflow pins immutable URLs, SHA-256 and exact byte counts in `catalog.json`. Do **not** hand-edit/submit generated catalog changes. Catalog updates are explicit, not automatic installs, and do not overwrite local/imported packages. [S5][S12]

## 4. Proposed Mocha/Blue mapping

**[Official Catppuccin guidance]** Base is the main pane; Crust/Mantle are secondary panes; Surface0–2 are surfaces; Text is body/headline; Subtext0/1 are labels; Overlay1 is subtle text; Base is the on-accent foreground; Blue is links; Green/Yellow/Red communicate success/warning/error. Legibility takes priority. These roles and hex values come from Catppuccin itself; their assignment to Serein keys below is **our recommendation**, not a published official Serein port. [C1][C2]

| Serein token | Proposed Mocha value | Rationale |
| --- | --- | --- |
| `base` | Crust `#11111b` | Serein's title strip/server rail, not its main chat pane |
| `sidebar` | Mantle `#181825` | Secondary lists |
| `chat` | Base `#1e1e2e` | Main conversation |
| `raised` | Surface0 `#313244` | Composer/cards/popouts |
| `hover` | Surface0 `#313244` | Quiet row hover; preserves Blue and muted-label contrast |
| `selected` | Surface0 `#313244` | Preserves contrast even when a selected row retains muted/Blue labels |
| `border` | Surface1 `#45475a` | Subtle separators; not a claim of sufficient focus-indicator contrast |
| `text_strong`, `text` | Text `#cdd6f4` | Body/headlines |
| `muted` | Subtext0 `#a6adc8` | Essential timestamps/labels remain readable |
| `link`, `accent`, `mention_text` | Blue `#89b4fa` | One fixed requested accent |
| `accent_text` | Base `#1e1e2e` | Dark foreground on Blue fills |
| `mention_bg` | Surface0 `#313244` | Exact opaque surface beneath Blue mention text |
| `positive` | Green `#a6e3a1` | Success |
| `warning` | Yellow `#f9e2af` | Warning |
| `danger` | Red `#f38ba8` | Error/destructive |

The shared name `base` is misleading: **Serein `base` → Catppuccin Crust**, whereas **Serein `chat` → Catppuccin Base**. Use semantic UI roles, not token-name matching. [S13][C1]

**Constraint takes precedence over translucency conventions:** the proposed table intentionally uses no alpha-suffixed colors, custom tints, calculated shades, white, or black. Catppuccin's general selection-opacity guideline is described above as upstream guidance, not permission to generate additional authored values. If testing shows a necessary non-palette value, stop and explain before using one.

**Computed contrast, not official published Catppuccin ratios:** using WCAG relative luminance on the official opaque Mocha hex values gives Base/Blue **7.79:1**, Text/Blue **1.46:1**, Text/Base **11.34:1**, Subtext0/Base **7.37:1**, Overlay1/Base **4.44:1**, and Blue/Surface0 **5.97:1**. WCAG's normal-text target is at least **4.5:1**. Therefore set `accent_text` explicitly to Base, do not use Text on solid Blue, and prefer Subtext0 over Overlay1 for small essential labels. Recalculate actual composited backgrounds and interactive states rather than assuming these ratios cover translucency, hover/selection, images, or the entire UI. [C2][W1]

### Post-research color review (`frontend-design`, color only)

The research agent has finished. Applying the supplied design skill only to color selection, the compact core is **Crust `#11111b`, Mantle `#181825`, Base `#1e1e2e`, Surface0 `#313244`, Text `#cdd6f4`, and Blue `#89b4fa`**. Surface1, Subtext0, Green, Yellow, and Red serve the specific interaction, hierarchy, and status roles in the table; they are not competing accents. No typography, layout, geometry, animation, or imagery changes are proposed.

**Brief review and revision:** the initial mapping used Surface1 for both hover and selected states. Review first proposed Surface0 for hover while retaining Surface1 for selection. Implementation contrast checks showed that selected rows retaining Blue or muted text would still be below the normal-text target, so the shipped mapping uses Surface0 for both states. Readability takes precedence over distinct fill levels; no intermediate shade is invented. Keep Blue for primary actions, links, and mentions rather than decorative tinting of every surface. Retain semantic Green/Yellow/Red rather than turning every status blue. All selected values are exact official Mocha entries. [C1][C2]

**Contrast qualification:** Blue/Surface1 is **4.33:1** and Subtext0/Surface1 is **4.10:1**, below the normal-text target; Surface2 would worsen those pairs, so neither is used as a selected surface. Serein's shared active-widget style uses `text_strong`, which maps to Text, but individual row consumers and derived states still require visual inspection. The local tests check key opaque foreground/background pairs, not every rendered state. [S6][C2][W1]

**Implementation gate resolved:** the user accepted the documented host-controlled exceptions before implementation. No off-palette authored value is needed or approved. No client modifications are made; any future proposal to author a non-palette color still requires stopping and explaining it first.

## 5. Minimal source-verified package example

This is a **schema illustration inside the report**, not the finished theme or a runtime-tested artifact. Its envelope/fields/colors match the inspected parser and official theme packages. It intentionally overrides only a few colors, so omitted tokens remain Serein defaults. Select **Dark** appearance to inspect it; this example does not force dark mode. A final port should explicitly cover all 18 tokens. [S3][S4][S17]

```json
{
  "manifest": {
    "api_version": 1,
    "id": "catppuccin-mocha-blue",
    "name": "Catppuccin Mocha — Blue",
    "version": "0.1.0",
    "author": "Your name",
    "license": "MIT",
    "source": "",
    "kind": "theme",
    "capabilities": [],
    "actions": []
  },
  "theme": {
    "dark": {
      "colors": {
        "chat": "#1e1e2e",
        "text": "#cdd6f4",
        "accent": "#89b4fa",
        "accent_text": "#1e1e2e",
        "link": "#89b4fa"
      }
    }
  }
}
```

Replace attribution and provide a real public HTTPS source before distribution/catalog submission; empty `source` is verified only for local themes. Save a future package with `.serein-extension`, not `.theme.css`; JSON has no comments, aliases, `$ref`, or named-palette indirection in this schema. [S3][S4]

## 6. Recommended implementation architecture, later

**[Recommendation]** Keep the eventual port deliberately small:

1. Ship **one** `catppuccin-mocha-blue.serein-extension`, with one stable `catppuccin-mocha-blue` identity. No flavor/accent selector, runtime plugin, Wasm, CSS adapter, or npm dependency is required.
2. Start with all 18 color keys and default native geometry. Use only exact opaque Mocha entries from the pinned official palette; no custom hex values, generated shades, alpha variants, or non-palette black/white. Omit optional backgrounds, blur, fonts, and preview-only metrics. Set the host to Dark and effects off during baseline testing. Explain the host-derived-state limitation before proceeding if renderer-wide purity is required.
3. For a strictly Mocha-only package, consider mirroring the **same complete Mocha/Blue values** into both `dark` and `light`, so system appearance changes cannot introduce light Serein fallback colors. This is still one flavor, not a Latte variant. The host retains mode-dependent rendering behavior, so test both modes and recommend Dark for the intended appearance. [S4][S6]
4. Maintain one fixed role table/palette source if generation is useful; otherwise checked-in JSON is sufficient. Do not add a multi-flavor generator for this request. If generating both mode maps, test their equality to avoid drift.
5. Add a concise installation/readme, MIT license with relevant Catppuccin notices, and screenshots under `assets/` when implementation is authorized. Catppuccin's port guide describes template conventions, catwalk previews and optional port review; do not present an independent port as officially adopted. Its generic four-flavor screenshot workflow need not expand this explicitly Mocha-only scope. [C3]
6. Prefer original mapping over copying a Discord CSS implementation. If code/assets are copied substantially, preserve their actual copyright/license notices and review derivative terms; merely being a “theme” does not erase upstream licenses. Catppuccin's palette is MIT (2021 Catppuccin), and its Discord port is separately MIT (2022 Catppuccin). [C3][C4][C5]

## 7. Validation and testing plan

**[Recommendation; not performed during this research]**

1. **Record the host**: exact Serein tag/commit, OS/architecture, appearance mode, built-in variant, effects setting, custom accent, and active appearance plugins. Do not claim minimum-version compatibility without testing that version.
2. **Static checks**: valid UTF-8 JSON; exact manifest fields; stable safe ID; theme kind; zero permissions/actions/Wasm; exactly the 18 known keys per final mode; every authored color an exact opaque entry from official Mocha, with no alpha/custom shades; Blue accent and Base `accent_text`; package-size bound. If mirroring, assert both mode maps match.
3. **Authoritative host validation**, from the pinned/matching Serein checkout:

   ```sh
   cargo run --locked -p extensions --example theme_import -- /absolute/path/catppuccin-mocha-blue.serein-extension
   cargo run --locked -p ui --example theme_api
   cargo run --locked -p serein --features demo -- --demo
   ```

   `theme_import` actually parses supplied files through the host. `theme_api` validates/applies the upstream Ocean fixture and exercises style bounds/reset; it does **not** automatically test our eventual package's appearance. A manifest-only checker is not sufficient for a theme package. [S18][S19]
4. **Synthetic UI inspection**: import manually in Themes; verify all columns, text/links, unread/selected/hover rows, composer, mentions, buttons, disabled controls, tooltips, menus, modal/profile/settings surfaces, code blocks, search, forum/thread views, and voice controls. Verify color meaning is not conveyed only by color. Use narrow/wide windows and several display scales.
5. **Contrast and rendering**: measure actual relevant foreground/background pairs, including selected/hovered raised controls, muted timestamps, keyboard focus and filled primary/destructive buttons. Record upstream-derived shades, alpha/compositing and hard-coded white separately from authored token values; do not “fix” contrast with a non-palette color without stopping for user approval. Compare both appearance modes if both are supplied; mode-specific egui text processing can still differ. [S6]
6. **Lifecycle**: import → use → restart persistence → switch built-in and back → reimport changed same-ID package → reset shortcut → reselect → disable. Ensure imported originals survive. Test invalid color/unknown token rejection without replacing the last good appearance. [S3][S16][S18]
7. **Interference/regression**: deliberately change user primary color; separately enable an appearance plugin; verify the documented source/docs accent discrepancy and overlay order on the target build. Repeat with transparency disabled and enabled only if transparency support will be advertised.
8. **Publishing**: test downloadable bytes, version/source/license metadata, and checksum; if seeking shop inclusion, run upstream catalog validation and provide licensed preview PNGs. Catppuccin README assets may prefer WebP, but Serein shop previews accept PNG/JPEG and upstream catalog tooling specifically documents same-stem PNG files—use the format required by each destination. [S5][S12][C3]

Current docs contain stale demo instructions: the extension guide's final paragraph claims demo cannot download public catalog content, while its opening sections and README say demo catalog browsing/downloads can use public GitHub. The authoring tutorial also omits `--features demo` in one launch command. Use the current README's explicit demo feature flag, avoid catalog browsing when strict offline operation is required, and do not equate “synthetic conversations” with a network-isolated process. [S1][S5][S9]

## 8. Implementation and completed validation

After the user accepted host-rendered exceptions, one color-only package was
created at `../catppuccin-mocha-blue.serein-extension`, with identical complete
Mocha maps for both modes, Blue accent, and Base on-accent text. The final selected
surface is Surface0 for the contrast reasons recorded above. No fonts, geometry,
plugins, effects, or external images are included.

On 2026-11-14:

- All **7** local tests passed (`python3 -m unittest discover -s tests -v`).
- Serein's actual `theme_import` example at the pinned `bedb57c0c8def62e736e8a4f03e0a5d248b22126`
  source baseline parsed the package and printed **Imported theme: Catppuccin
  Mocha — Blue (catppuccin-mocha-blue)**, followed by a successful path-safety check.
- No theme was installed into the user's client, and no native visual/lifecycle
  test is claimed. The remaining checklist above still applies before release.

For public distribution, the package now identifies **LyKhoris** as its author
and uses `https://github.com/LyKhoris/SereinCatppuccin` as its source. The original
local-import example above intentionally illustrates the empty-source option.

## Primary-source references

All accessed 2026-11-14. Serein source links are immutable commit permalinks unless identified as live endpoints.

- **[S0]** [Serein baseline commit](https://github.com/ViceVerse-cz/Serein/commit/bedb57c0c8def62e736e8a4f03e0a5d248b22126).
- **[S1]** [Serein README](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/README.md).
- **[S2]** [Platform support, especially lines 37–45](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/platform-support.md#L37-L45).
- **[S3]** [Theme API specification](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/theme-api.md).
- **[S4]** [Host serialized types and validation](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/extensions/src/lib.rs): manifest/theme/package types at lines 234–388; manifest validation 829–940; colors/theme/package parsing 943–1130.
- **[S5]** [Community extensions / host contract / lifecycle](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extensions.md).
- **[S6]** [Native theme implementation](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/ui/src/design.rs): [recoloring and accent precedence](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/ui/src/design.rs#L788-L883), [shared styles / selection / cursor](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/ui/src/design.rs#L1099-L1209).
- **[S7]** [Cargo workspace/dependencies](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/Cargo.toml#L1-L50).
- **[S8]** [Wasm runtime implementation](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/extensions/src/runtime.rs).
- **[S9]** [Plugin authoring/examples guide](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/examples/extensions/README.md).
- **[S10]** [Live official releases API](https://api.github.com/repos/ViceVerse-cz/Serein/releases?per_page=5), [observed nightly](https://github.com/ViceVerse-cz/Serein/releases/tag/v1.0.0-nightly.20261113.90).
- **[S11]** [SDK overview](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extension-sdk-overview.md), [input/data reference](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extension-sdk-reference.md), [outputs/actions reference](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extension-sdk-actions.md), [troubleshooting](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extension-sdk-troubleshooting.md).
- **[S12]** [Canonical catalog, publishing, migration and provenance](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/extensions/README.md).
- **[S13]** [Design guide](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/design.md).
- **[S14]** [Official wiki home, live older-preview banner](https://github.com/ViceVerse-cz/Serein/wiki).
- **[S15]** [Official wiki: Creating a Theme](https://github.com/ViceVerse-cz/Serein/wiki/Creating-a-Theme).
- **[S16]** [Desktop installation/import/store implementation](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/apps/desktop/src/extensions.rs): import 804–822, install/copy/grants 949–1089, theme lifecycle tests beginning at 2203.
- **[S17]** [Official complete color-only theme example](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/extensions/themes/latte.serein-extension). Its name “Latte” does not make it the Catppuccin palette.
- **[S18]** [Authoritative theme file checker](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/extensions/examples/theme_import.rs).
- **[S19]** [Offline native theme API example/check](https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/ui/examples/theme_api.rs).
- **[C1]** [Official Catppuccin style guide](https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md) (live).
- **[C2]** [Official Catppuccin palette JSON, v1.8.0, pinned](https://github.com/catppuccin/palette/blob/07d02aa110ef9eb7e7427afca5c73ba9cf7f8ebd/palette.json).
- **[C3]** [Official Catppuccin port creation guide](https://github.com/catppuccin/catppuccin/blob/main/docs/port-creation.md) (live).
- **[C4]** [Official Catppuccin Discord port README](https://github.com/catppuccin/discord/blob/main/README.md), [license](https://github.com/catppuccin/discord/blob/main/LICENSE) (live; separate web/CSS port).
- **[C5]** [Catppuccin palette MIT license, pinned](https://github.com/catppuccin/palette/blob/07d02aa110ef9eb7e7427afca5c73ba9cf7f8ebd/LICENSE).
- **[W1]** [W3C: Understanding WCAG 2.2 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

[S0]: https://github.com/ViceVerse-cz/Serein/commit/bedb57c0c8def62e736e8a4f03e0a5d248b22126
[S1]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/README.md
[S2]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/platform-support.md
[S3]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/theme-api.md
[S4]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/extensions/src/lib.rs
[S5]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extensions.md
[S6]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/ui/src/design.rs
[S7]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/Cargo.toml
[S8]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/extensions/src/runtime.rs
[S9]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/examples/extensions/README.md
[S10]: https://github.com/ViceVerse-cz/Serein/releases/tag/v1.0.0-nightly.20261113.90
[S11]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/extension-sdk-overview.md
[S12]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/extensions/README.md
[S13]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/docs/design.md
[S14]: https://github.com/ViceVerse-cz/Serein/wiki
[S15]: https://github.com/ViceVerse-cz/Serein/wiki/Creating-a-Theme
[S16]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/apps/desktop/src/extensions.rs
[S17]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/extensions/themes/latte.serein-extension
[S18]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/extensions/examples/theme_import.rs
[S19]: https://github.com/ViceVerse-cz/Serein/blob/bedb57c0c8def62e736e8a4f03e0a5d248b22126/crates/ui/examples/theme_api.rs
[C1]: https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md
[C2]: https://github.com/catppuccin/palette/blob/07d02aa110ef9eb7e7427afca5c73ba9cf7f8ebd/palette.json
[C3]: https://github.com/catppuccin/catppuccin/blob/main/docs/port-creation.md
[C4]: https://github.com/catppuccin/discord/blob/main/README.md
[C5]: https://github.com/catppuccin/palette/blob/07d02aa110ef9eb7e7427afca5c73ba9cf7f8ebd/LICENSE
[W1]: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

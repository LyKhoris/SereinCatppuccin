# Catppuccin Mocha for Serein

A native [Serein](https://github.com/ViceVerse-cz/Serein) theme using the official
[Catppuccin Mocha palette](https://github.com/catppuccin/palette/blob/07d02aa110ef9eb7e7427afca5c73ba9cf7f8ebd/palette.json)
with **Blue (`#89b4fa`)** as its accent.

## Install

1. Download [`catppuccin-mocha-blue.serein-extension`](https://github.com/LyKhoris/SereinCatppuccin/releases/latest/download/catppuccin-mocha-blue.serein-extension).
2. In Serein, open **Settings → Themes** and import the file.
3. Complete the install/use flow; choose **Use theme** if the theme is inactive.
4. Select **Dark** appearance and turn off **Transparency & blur** for the intended
   opaque colors. Restart Serein if you change that effects switch.

Both appearance maps contain the same Mocha colors, so switching to Light does
not introduce a different palette. Serein still has mode-dependent rendering;
Dark is recommended.

Use **Reset** or **Ctrl+Shift+F12** to return to the built-in appearance.
This keeps the theme installed. **Disable** removes its installed copy, not your
downloaded file.

This is JSON, not BetterDiscord CSS. No plugin, permissions, build step, fonts,
images, or layout changes are required. All 18 color tokens are supplied.

## Colors

| Role | Official Mocha color |
| --- | --- |
| Window frame and server rail | Crust `#11111b` |
| Sidebars | Mantle `#181825` |
| Conversation | Base `#1e1e2e` |
| Raised, hovered, and selected surfaces | Surface0 `#313244` |
| Borders | Surface1 `#45475a` |
| Main text | Text `#cdd6f4` |
| Secondary text | Subtext0 `#a6adc8` |
| Accent, links, and mention text | Blue `#89b4fa` |
| Text on solid accent | Base `#1e1e2e` |
| Success / warning / danger | Green `#a6e3a1` / Yellow `#f9e2af` / Red `#f38ba8` |

Selected surfaces deliberately stay at Surface0: Blue and secondary text on
Surface1 fall below the 4.5:1 normal-text contrast target. Surface0 preserves
readability where the host reuses those text colors. Hover and selection share
a fill; this theme does not invent an intermediate shade to distinguish them.

### Native rendering limitations

Every authored color is an exact, opaque official Mocha value. Serein itself
generates some state colors and hard-codes white on controls such as switch
knobs and destructive-button labels. Those accepted host-controlled exceptions
cannot be overridden by this theme. Pastel danger fills with white labels may
have insufficient contrast; no renderer-wide accessibility guarantee is made.

Other appearance plugins can override theme values. Accent precedence also
differs between the inspected source and its documentation. See the
[research and compatibility notes](serein-research.md) for the pinned
Serein baseline, source references, and manual testing checklist.

## Validate

Run the dependency-free checks from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

They check package structure, complete identical mode maps, exact palette
membership, intended role assignments, and key opaque text contrast pairs.
They do not replace Serein's parser or visual testing.

For authoritative parser validation, from a matching Serein source checkout:

```sh
cargo run --locked -p extensions --example theme_import -- /absolute/path/catppuccin-mocha-blue.serein-extension
```

No installed-client visual test is claimed. The package identifies LyKhoris as
the author and links to this public source repository. Test the target Serein
release before claiming compatibility or submitting to its catalog.

### Verified baseline

On 2026-11-14, all **7 local tests passed**, and Serein's own `theme_import`
example successfully parsed and validated this package at commit
[`bedb57c0c8def62e736e8a4f03e0a5d248b22126`](https://github.com/ViceVerse-cz/Serein/commit/bedb57c0c8def62e736e8a4f03e0a5d248b22126).
This verifies the package format, not installed-release compatibility or native
visual appearance.

## Credits and license

Independent port; not an officially adopted Catppuccin port or a Serein product.
Palette by [Catppuccin](https://github.com/catppuccin). Distributed under the
[MIT license](../LICENSE).

# Vendored runtime — reveal.js 4.6.1

Committed so that a deck opens from `file://` with **no network**: a lecture hall
without wifi still presents. Same policy as `research-report/assets/vendor/`.

Everything below comes from the npm package `reveal.js@4.6.1`, redistributed
unmodified (see `THIRD_PARTY_NOTICES.md`). Re-pin with `bash scripts/vendor.sh`:
it re-downloads every path in the two tables, sanity-checks the sizes, recomputes
the hashes and rewrites the rows between the markers.

## Core

Base: `https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/`

<!-- BEGIN-CORE-TABLE -->
| file | source path | sha256 |
|---|---|---|
| `reveal.js` | `dist/reveal.js` | `73d4b64d59eded6de6a49500e7b709eb8d92c0d1d88d911319ce551c31341e9f` |
| `reveal.css` | `dist/reveal.css` | `fa4713396db8274bc0f1def50767464b6d98e61f4f83d17f4de6417210b25901` |
| `white.css` | `dist/theme/white.css` | `bf59df9ecd8563ac1da668571397dd454048f493e0feddcc565df7eedc40fad4` |
| `LICENSE` | `LICENSE` | `b7cb6bd5ddfd103bf1795467346d95f2a20eb027db0c3fc96255e8a3434dbdb5` |
<!-- END-CORE-TABLE -->

## Theme fonts

`white.css` begins with `@import url(./fonts/source-sans-pro/source-sans-pro.css)`,
and CSS `@import` is fetched eagerly — so the theme 404s its own font stylesheet unless
the directory sits next to it. The house decks override `font-family`, so the fonts are
never *used*, but they must *resolve*: a 404 is a console error and the gate counts
console errors.

<!-- BEGIN-FONT-TABLE -->
| file | source path | sha256 |
|---|---|---|
| `fonts/source-sans-pro/source-sans-pro.css` | `dist/theme/fonts/source-sans-pro/source-sans-pro.css` | `5292b4fb38f4e609bf20cd98b3e5c039dbd7271d1c9174302305fbaaf42035cc` |
| `fonts/source-sans-pro/source-sans-pro-regular.eot` | `dist/theme/fonts/source-sans-pro/source-sans-pro-regular.eot` | `dce8869d25c3abcecb33a3486a3c70bb76aed17c21a74069ee83949b1d209c9b` |
| `fonts/source-sans-pro/source-sans-pro-regular.woff` | `dist/theme/fonts/source-sans-pro/source-sans-pro-regular.woff` | `d4eaa48ba450f4dd2d024ab5b0e895c73c81475718e5453fd1890254c16b7a57` |
| `fonts/source-sans-pro/source-sans-pro-regular.ttf` | `dist/theme/fonts/source-sans-pro/source-sans-pro-regular.ttf` | `c1865d89d798bc2119872b17774361c7406974b9568121a617007e02af344981` |
| `fonts/source-sans-pro/source-sans-pro-italic.eot` | `dist/theme/fonts/source-sans-pro/source-sans-pro-italic.eot` | `ad4b0799608b5dc860cc3bd7ff4781f2d9e13144e48a2e3d9321ce57c5a12f2a` |
| `fonts/source-sans-pro/source-sans-pro-italic.woff` | `dist/theme/fonts/source-sans-pro/source-sans-pro-italic.woff` | `05d3615fdbe7d35c62d6a1308dc48e3985016b69e65926ed37b99fe7e6b297dc` |
| `fonts/source-sans-pro/source-sans-pro-italic.ttf` | `dist/theme/fonts/source-sans-pro/source-sans-pro-italic.ttf` | `d13268affb2204223a1b6b8483afd989a0e2b20bff853eae05fe5d0d32de8ed9` |
| `fonts/source-sans-pro/source-sans-pro-semibold.eot` | `dist/theme/fonts/source-sans-pro/source-sans-pro-semibold.eot` | `ebb8918da92bae172dfe322a3947929b3df2330dccc6f13c7d8e8ed3815e1696` |
| `fonts/source-sans-pro/source-sans-pro-semibold.woff` | `dist/theme/fonts/source-sans-pro/source-sans-pro-semibold.woff` | `b0abd2736335424f9fd3eb27974a36d03783b3db141e0801dca7d3a635218b46` |
| `fonts/source-sans-pro/source-sans-pro-semibold.ttf` | `dist/theme/fonts/source-sans-pro/source-sans-pro-semibold.ttf` | `a53e27232eff5f0bc1ba1c0af7e0759f0aaaf5c0636370b4c54f83c4652ba924` |
| `fonts/source-sans-pro/source-sans-pro-semibolditalic.eot` | `dist/theme/fonts/source-sans-pro/source-sans-pro-semibolditalic.eot` | `dfe0b47abfa0fdb0504d7be14015fa3f1cf9647b97ffd8b3bfcceb25c60f4fa6` |
| `fonts/source-sans-pro/source-sans-pro-semibolditalic.woff` | `dist/theme/fonts/source-sans-pro/source-sans-pro-semibolditalic.woff` | `7225cacc06c2f360367c138daa4ce727c2a0d26e42875b1f9e802f181fdb81c5` |
| `fonts/source-sans-pro/source-sans-pro-semibolditalic.ttf` | `dist/theme/fonts/source-sans-pro/source-sans-pro-semibolditalic.ttf` | `e8ec22b619599ef4088c788ec410ea3e70481acc9ec43cc0a7fcd00da6441646` |
<!-- END-FONT-TABLE -->

The `.eot`/`.ttf` files are never requested by Chrome (`.woff` is listed first and wins);
they are kept so the bundle is a faithful copy of what the theme asks for. Total ≈ 1.9 MB.
The OFL text for the fonts is `fonts/source-sans-pro/LICENSE.md`, vendored beside them.

## Notes

**Upstream quirk, do not "fix":** the 4.6.1 `dist/` bundles still carry the banner
`reveal.js 4.6.0` and the internal literal `4.6.0`, although `package.json` says
`4.6.1`. The npm tarball is 4.6.1; the version string inside `dist/` was not bumped.
`grep -c 4.6.0 reveal.js` returning 2 is expected.

`LICENSE` is at the package root, not under `dist/` — requesting `dist/LICENSE` from the
CDN returns a 60-byte error page, which is why `vendor.sh` lists it as `LICENSE`.

# Third-party notices

## reveal.js 4.6.1

MIT License. Copyright (C) 2011-2023 Hakim El Hattab, http://hakim.se, and
reveal.js contributors. Full text: `LICENSE` in this directory.

Vendored unmodified from the npm package `reveal.js@4.6.1` for offline
presentation: `dist/reveal.js`, `dist/reveal.css`, `dist/theme/white.css`, and the
theme's font stylesheet plus font binaries under `dist/theme/fonts/`. Decks in this
skill load these files by relative path from their own `vendor/reveal/` copy;
nothing else from the package is redistributed.

## Source Sans Pro

The font binaries under `fonts/source-sans-pro/` are **Source Sans Pro**,
Copyright 2010–2024 Adobe (http://www.adobe.com/), with Reserved Font Name
'Source'. Licensed under the **SIL Open Font License, Version 1.1**; the full text
is `fonts/source-sans-pro/LICENSE.md`, vendored alongside the fonts as the OFL
requires. The fonts are not modified.

They are redistributed because `white.css` imports its font stylesheet and CSS
`@import` is fetched eagerly; a deck that presents offline must carry them or log a
404. The house decks override `font-family` and so do not use Source Sans Pro for
text — but the licence travels with the bytes.

## Our own work

The skill's own code and text: see the repository `LICENSE` (MIT).
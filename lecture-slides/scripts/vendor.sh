#!/bin/bash
# vendor.sh — (re)download the pinned reveal.js runtime and rewrite its manifest.
#
# The deck must present with no network, so reveal.js lives in assets/vendor/reveal/.
# This script re-fetches exactly the paths the manifest lists (core + the theme's font
# stylesheet and font binaries, which `white.css` imports eagerly), sanity-checks each file,
# recomputes the sha256 and rewrites both tables in MANIFEST.md.
#
#   bash scripts/vendor.sh              # verify and refresh
#   bash scripts/vendor.sh --check      # verify only; nonzero if a hash would change
#
# Reference: assets/vendor/reveal/MANIFEST.md, assets/vendor/reveal/THIRD_PARTY_NOTICES.md.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/assets/vendor/reveal"
BASE="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1"
MODE="apply"
[ "${1:-}" = "--check" ] && MODE="check"

# "package-relative source path|local path|minimum bytes"
# NB: LICENSE sits at the package root — requesting dist/LICENSE returns a 60-byte error page.
FILES="
dist/reveal.js|reveal.js|50000
dist/reveal.css|reveal.css|5000
dist/theme/white.css|white.css|5000
LICENSE|LICENSE|500
dist/theme/fonts/source-sans-pro/source-sans-pro.css|fonts/source-sans-pro/source-sans-pro.css|500
dist/theme/fonts/source-sans-pro/source-sans-pro-regular.eot|fonts/source-sans-pro/source-sans-pro-regular.eot|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-regular.woff|fonts/source-sans-pro/source-sans-pro-regular.woff|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-regular.ttf|fonts/source-sans-pro/source-sans-pro-regular.ttf|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-italic.eot|fonts/source-sans-pro/source-sans-pro-italic.eot|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-italic.woff|fonts/source-sans-pro/source-sans-pro-italic.woff|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-italic.ttf|fonts/source-sans-pro/source-sans-pro-italic.ttf|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-semibold.eot|fonts/source-sans-pro/source-sans-pro-semibold.eot|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-semibold.woff|fonts/source-sans-pro/source-sans-pro-semibold.woff|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-semibold.ttf|fonts/source-sans-pro/source-sans-pro-semibold.ttf|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-semibolditalic.eot|fonts/source-sans-pro/source-sans-pro-semibolditalic.eot|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-semibolditalic.woff|fonts/source-sans-pro/source-sans-pro-semibolditalic.woff|20000
dist/theme/fonts/source-sans-pro/source-sans-pro-semibolditalic.ttf|fonts/source-sans-pro/source-sans-pro-semibolditalic.ttf|20000
"

mkdir -p "$DEST/fonts/source-sans-pro" || exit 2
TMP="$(mktemp -d)" || exit 2
trap 'rm -rf "$TMP"' EXIT

changed=0
rows=""
while IFS='|' read -r src local minb; do
  [ -z "${src:-}" ] && continue
  out="$TMP/$(basename "$local")"
  curl -sSL --max-time 180 -o "$out" "$BASE/$src" || { echo "FAIL download $src" >&2; exit 1; }
  size=$(stat -f%z "$out" 2>/dev/null || stat -c%s "$out")
  if [ "$size" -lt "$minb" ]; then
    echo "FAIL $src is only $size bytes (expected >= $minb) — bad download or upstream change" >&2
    exit 1
  fi
  old=""
  [ -f "$DEST/$local" ] && old=$(shasum -a 256 "$DEST/$local" | awk '{print $1}')
  new=$(shasum -a 256 "$out" | awk '{print $1}')
  [ "$old" != "$new" ] && echo "CHANGED $local  $old -> $new"
  [ "$old" != "$new" ] && changed=$((changed+1))
  if [ "$MODE" = "apply" ]; then
    mkdir -p "$DEST/$(dirname "$local")"
    cp "$out" "$DEST/$local"
    chmod 644 "$DEST/$local"
  fi
  rows="$rows$local|$new|$src
"
done <<EOF
$(echo "$FILES" | sed '/^$/d')
EOF

echo "files: $(echo "$FILES" | sed '/^$/d' | wc -l | tr -d ' ')  changed: $changed"
if [ "$MODE" = "check" ]; then
  [ "$changed" -eq 0 ] && echo "verify-only: bundle is byte-identical to the pin" || exit 1
  exit 0
fi

# ---- rewrite the rows between the two table markers, keeping every word of prose
python3 - "$DEST" "$rows" <<'PY'
import sys, pathlib
dest, rows = pathlib.Path(sys.argv[1]), sys.argv[2]
data = [r.split("|") for r in rows.strip().splitlines() if r.strip()]
core = {"reveal.js", "reveal.css", "white.css", "LICENSE"}

def block(pairs):
    return ("| file | source path | sha256 |\n|---|---|---|\n"
            + "\n".join("| `%s` | `%s` | `%s` |" % (l, s, h) for l, h, s in pairs))

def splice(text, begin, end, body):
    a, b = text.index(begin), text.index(end)
    return text[:a + len(begin)] + "\n" + body + "\n" + text[b:]

core_rows = [(r[0], r[1], r[2]) for r in data if r[0] in core]
font_rows = [(r[0], r[1], r[2]) for r in data if r[0] not in core]
m = dest / "MANIFEST.md"
text = m.read_text(encoding="utf-8")
text = splice(text, "<!-- BEGIN-CORE-TABLE -->", "<!-- END-CORE-TABLE -->", block(core_rows))
text = splice(text, "<!-- BEGIN-FONT-TABLE -->", "<!-- END-FONT-TABLE -->", block(font_rows))
m.write_text(text, encoding="utf-8")
print("rewrote %s (%d core + %d font rows)" % (m, len(core_rows), len(font_rows)))
PY
echo "vendor: ok"

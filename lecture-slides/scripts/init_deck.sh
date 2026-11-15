#!/bin/bash
# init_deck.sh — scaffold one lecture's deck directory the way the course lays them out.
#
#   bash scripts/init_deck.sh slides/lecture9/dsh --name lecture9 --title "The Hubble Constant"
#   bash scripts/init_deck.sh /tmp/try --name lecture99 --title "Test" --plan 第99讲课程框架 --force
#
# Produces (existing files are never clobbered without --force):
#
#   TARGET/<name>.html      from templates/deck.html, title + kicker rewritten
#   TARGET/vendor/reveal/   the pinned runtime, INCLUDING fonts/ (else white.css 404s its @import)
#   TARGET/assets/          empty + FIGURE_SOURCES.md
#   TARGET/render/          empty (render_deck.py writes slide-NN.png here)
#   TARGET/exercise/        empty
#   TARGET/<plan>.md        only with --plan, from templates/plan.zh-CN.md
#
# The template's own paths are `vendor/reveal/...`, relative to the deck — so the copy is
# already correct and is verified, not assumed.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "$#" -lt 1 ]; then
  echo "usage: init_deck.sh TARGET_DIR [--name lectureN] [--title \"Deck Title\"] [--plan NAME] [--force]" >&2
  exit 2
fi

TARGET="$1"; shift
NAME="lectureN"; TITLE="Deck Title"; PLAN=""; FORCE=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --name)  NAME="${2:-}"; shift 2 ;;
    --title) TITLE="${2:-}"; shift 2 ;;
    --plan)  PLAN="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

DECK="$TARGET/$NAME.html"
if [ -e "$DECK" ] && [ "$FORCE" -ne 1 ]; then
  echo "refusing to overwrite $DECK — pass --force to replace it" >&2
  exit 1
fi

mkdir -p "$TARGET/assets" "$TARGET/render" "$TARGET/exercise" || exit 2

# ---- the deck itself: title, kicker, both languages' conventions are ours to fill in
python3 - "$ROOT/templates/deck.html" "$DECK" "$TITLE" "$NAME" <<'PY'
import sys, re, pathlib
src, out, title, name = sys.argv[1:5]
t = pathlib.Path(src).read_text(encoding="utf-8")
t = t.replace("<title>Lecture N &middot; Title Goes Here</title>",
              "<title>%s</title>" % title.replace("&", "&amp;"))
t = re.sub(r'(<p class="kicker">)[^<]*(</p>)',
           lambda m: m.group(1) + "Course Name &middot; %s" % name.replace("lecture", "Lecture ")
           + m.group(2), t, count=1)
t = re.sub(r'<h1>DECK TITLE<br>IN TWO LINES</h1>',
           "<h1>%s</h1>" % title.upper(), t, count=1)
pathlib.Path(out).write_text(t, encoding="utf-8")
print("wrote", out)
PY
[ $? -ne 0 ] && exit 1

# ---- the pinned runtime, fonts included
mkdir -p "$TARGET/vendor"
cp -R "$ROOT/assets/vendor/reveal" "$TARGET/vendor/reveal" || exit 1
if [ ! -f "$TARGET/vendor/reveal/fonts/source-sans-pro/source-sans-pro.css" ]; then
  echo "vendor copy is missing the theme fonts — white.css will 404 its @import" >&2
  exit 1
fi

# ---- the documents
[ -f "$TARGET/assets/FIGURE_SOURCES.md" ] || cp "$ROOT/templates/FIGURE_SOURCES.md" "$TARGET/assets/"
if [ -n "$PLAN" ]; then
  [ -f "$TARGET/$PLAN.md" ] && [ "$FORCE" -ne 1 ] || cp "$ROOT/templates/plan.zh-CN.md" "$TARGET/$PLAN.md"
fi

echo "scaffolded $TARGET  (name=$NAME)"
echo "note: the template names five placeholder figures under assets/; until you put real"
echo "      files there the render reports 5 broken images and 9 console errors. That is the"
echo "      scaffold being honest, not a broken deck."
echo "next:"
echo "  python3 $ROOT/scripts/render_deck.py --deck $DECK --strict"
echo "  python3 $ROOT/scripts/audit_deck.py --deck $DECK"
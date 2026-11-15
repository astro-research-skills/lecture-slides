#!/bin/bash
# fetch_pdf.sh <arxiv-id> <out.pdf> [min-pages]
#
# Fetch a paper's PDF from arXiv and refuse to hand back a truncated or error page: the
# renderer is only ever as good as the PDF, so a silent 1-page "PDF" from an error response
# must fail loudly. Up to four attempts, `pdfinfo` must parse it, and it must have at least
# `min-pages` pages.
#
#   bash fetch_pdf.sh 0710.3740 /tmp/liwhite2008.pdf 6
#   pdftoppm -r 300 -png /tmp/liwhite2008.pdf /tmp/pg
#   python3 crop_fig.py --page /tmp/pg-03.png --out assets/figure.png
#
# Reference: references/figures.md §1 (arXiv is rung 1 of the sourcing ladder).
set -u

if [ "$#" -lt 2 ]; then
  echo "usage: fetch_pdf.sh <arxiv-id> <out.pdf> [min-pages]" >&2
  exit 2
fi

id="$1"; out="$2"; minpg="${3:-1}"

mkdir -p "$(dirname "$out")" 2>/dev/null || true

for try in 1 2 3 4; do
  curl -sL --retry 1 --max-time 120 -o "$out" "https://arxiv.org/pdf/${id}"
  if pdfinfo "$out" >/dev/null 2>&1; then
    pg=$(pdfinfo "$out" | awk '/^Pages:/{print $2}')
    if [ "${pg:-0}" -ge "$minpg" ]; then
      echo "OK $id -> $out (${pg}p, $(stat -f%z "$out" 2>/dev/null || stat -c%s "$out") bytes)"
      exit 0
    fi
    echo "retry $try: $id has ${pg:-0} page(s), need >= $minpg" >&2
  else
    echo "retry $try: $id is not a readable PDF (size=$(stat -f%z "$out" 2>/dev/null || echo 0))" >&2
  fi
  sleep 3
done

echo "FAIL $id" >&2
rm -f "$out"
exit 1
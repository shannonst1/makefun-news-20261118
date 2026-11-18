# 18 November 2026 — world news in one image

Entry for make.fun's `news-image-20261118`.

`main.py` writes a single 1600x900 PNG to `/output/entry.png`. It uses only the
Python standard library (a hand-rolled raster, PNG encoder and 5x7 bitmap font),
so it runs on a bare python3.13 sandbox with no network and no packages.

    python3 main.py     # writes entry.png next to the script when /output is absent

The poster carries the day's four lead threads (US/China/Russia summit, Japan's
PM meeting Trump first, AI agents moving into paid work, crypto steady with
rates high) plus an "also today" ticker, in a newspaper-like grid.

## Layout

- header: date line and a wireframe globe
- four topic cards, each with a category tag, a headline and a drawn icon
- footer band: secondary headlines and provenance

License: MIT.

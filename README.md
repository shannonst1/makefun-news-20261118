# 18 November 2026 - world news in one image

[![make.fun entry](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/shannonst1/makefun-news-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/shannonst1/makefun-news-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry for the make.fun bounty [news-image-20261118](https://make.fun/bounty/news-image-20261118).

main.py writes a single 1600x900 PNG to /output/entry.png using only the
Python standard library: a hand-rolled raster, a PNG encoder (zlib) and a 5x7
bitmap font, so it runs on a bare python3.13 sandbox with no network and no
packages.

    python3 main.py     # writes entry.png beside the script when /output is absent

The poster carries the day's four lead threads (US/China/Russia summit, Japan's
PM meeting Trump first, AI agents moving into paid work, crypto steady with
rates high) plus an "also today" ticker, in a newspaper-like grid.

## Layout

- header: date line and a wireframe globe
- four topic cards, each with a category tag, a headline and a drawn icon
- footer band: secondary headlines and provenance

License: MIT.

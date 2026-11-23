# Chukwunedum Mejeha · BIM Technician portfolio

Live site: https://chukwunedum-mejeha.vercel.app
Repository: https://github.com/mej94/BiM_-Portfolio-

A hand built static site. No framework, no page builder, no trackers.

## How it is built

1. `tools/capture.py` runs the same Python page generators that produce the A3 portfolio PDF, with a recording stand in for their layout library, and writes every page's text, figures and captions to `content.json`.
2. `tools/measure.js` opens each rendered PDF page in headless Chromium (Playwright) and records the true size and position of every figure, so the web layout keeps the editorial grid of the printed sheets (`boxes.json`).
3. `tools/build_site.py` turns that data into HTML: bands and column stacks on a nine column evidence grid, before and after sliders for matched screenshot pairs, WebP images through Pillow, and a command palette index.
4. `assets/site.js` is one vanilla ES module: a live wireframe building drawn in Canvas 2D with pulsing clash points and a moving section plane, a typed terminal summary, count up figures, scroll reveal and scrollspy with IntersectionObserver, a zoom and pan lightbox with pinch support, keyboard driven command palette (Ctrl K) and a persisted dark theme.

Hosted on Vercel as static files (`vercel.json` sets clean URLs, caching and security headers).

## Rebuild

```
python3 tools/build_site.py
```

Designed and developed by Chukwunedum Mejeha.

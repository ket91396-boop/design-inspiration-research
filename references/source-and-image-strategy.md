# Source And Image Strategy

Load this before live research or HTML report generation.

## Source Priority

- Primary design sources: Behance, Dribbble, Fonts In Use, Typewolf, Mobbin, Land-book, Awwwards.
- Primary photo/material sources: Unsplash, Pexels, official brand/media pages.
- Secondary discovery sources: Pinterest, curated blogs, agency portfolios, museum/archive pages.
- Supplement only: template/material marketplaces, stock-asset marketplaces, generic listicles.

Do not let thumbnail availability outrank source quality.

## Image Extraction Policy

Default sequence:

1. Keep the reference page URL.
2. Use `scripts/prepare_report_images.py` to try same-page `og:image`, `twitter:image`, `<img>`, and direct image candidates.
3. If no usable same-page image is found, leave `image` empty.
4. Keep the reference if the page is still design-useful.
5. Do not screenshot by default.

Screenshots are allowed only when the user explicitly asks for screenshot-backed cards and accepts slower generation.

## Site Expectations

- Behance: project pages often expose metadata images, but some pages require browser-rendered content or block static fetches. Keep the project link if extraction fails.
- Dribbble: shot pages can expose preview images, but markup changes and access controls are common. Keep the shot link if extraction fails.
- Unsplash: photo pages often expose image metadata or CDN URLs, but hotlinking and URL parameters can shift. Prefer same-page extracted images; otherwise keep the photo page.
- Pexels: photo pages often expose preview images, but static fetches may not always expose the intended image. Keep the page if extraction fails.
- Pinterest: often poor for direct extraction and can duplicate images. Prefer it for discovery, not as the main image source in reports.

## Failure Mode

If image preparation returns warnings, do not replace missing images with unrelated thumbnails. Fix only when a same-page image is available or a better reference page exists.

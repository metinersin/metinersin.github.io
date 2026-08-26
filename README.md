# metinersin.github.io

The source for [Metin Ersin Arıcan's academic website](https://metinersin.github.io). The site is written in [Quarto](https://quarto.org/) and deployed to GitHub Pages from the `main` branch by GitHub Actions. It uses the default `metinersin.github.io` address; there is no custom-domain configuration.

## Local development

Install Quarto 1.10 or newer, then use the repository wrappers:

```sh
make build
make preview
make doctor
```

- `make build` renders the production site to `_site/`.
- `make preview` serves a live preview at `http://127.0.0.1:4000`.
- `make doctor` checks the Quarto installation and performs a clean render.

The generated `_site/` directory is intentionally ignored. GitHub Actions installs Quarto, renders the site, and uploads `_site/` as a Pages artifact after each push to `main`.

## Site structure

- `_quarto.yml` contains navigation, metadata, rendering, and resource settings.
- `index.qmd`, `research.qmd`, `teaching.qmd`, and `notes.qmd` are the primary pages.
- `cv/index.qmd` is the accessible HTML CV; `output/pdf/Metin_Ersin_Arican_CV.pdf` is its downloadable counterpart.
- `blog/` contains migrated mathematical notes. Their nested paths preserve the URLs from the former Jekyll site.
- `student-distribution-tool/` is a standalone browser application copied unchanged into the rendered site.
- `styles.css` contains the restrained visual theme layered on Quarto's Cosmo theme.

## Add a note

Create an `index.qmd` below a descriptive directory in `blog/` and include at least:

```yaml
---
title: "Note title"
author: "Metin Ersin Arıcan"
date: 2026-08-09
description: "One-sentence summary used by the listing and feed."
categories: [mathematics, topic]
---
```

Add the source path to the `listing.contents` array in `notes.qmd` when the note is polished enough to publish.

Quarto supports inline math with `$...$` and display math with `$$...$$`. The shared MathJax configuration defines these site-wide commands:

- `\RR` for `\mathbb{R}`
- `\NN` for `\mathbb{N}`
- `\diag` for `\operatorname{Diag}`

For example: `Let $f\colon \RR \to \RR$ and $n \in \NN$.`

## Update the CV

Keep the facts in `cv/index.qmd` and `script/build_cv_pdf.py` aligned. Regenerate the downloadable file with a Python environment containing ReportLab:

```sh
python3 script/build_cv_pdf.py
```

Then render the site and inspect both the HTML page and PDF before publishing.

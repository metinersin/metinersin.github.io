# metinersin.github.io

This repository contains the source for [metinersin.github.io](https://metinersin.github.io), a personal academic website built with Jekyll and hosted on GitHub Pages.

## Quick start

Use the repository scripts rather than running `bundle exec jekyll` directly. The scripts select a compatible Ruby version and the Bundler version recorded in `Gemfile.lock`.

```sh
make preview
```

Open <http://127.0.0.1:4000> in a browser. The preview process watches most source files and rebuilds the site when they change. Restart it after changing `_config.yml`.

Before publishing, run the production build:

```sh
make build
```

The generated site is written to `_site/`. Do not edit files in `_site/`; that directory is replaced on every build.

For a complete Ruby, Bundler, Jekyll, and build check, run:

```sh
make doctor
```

## Repository structure

| Path | Purpose |
| --- | --- |
| `_pages/` | Main pages such as Home, CV, Publications, Notes, and Contact |
| `_posts/` | Dated blog posts |
| `_data/projects.yml` | Project entries displayed on the Projects page |
| `_layouts/default.html` | Shared page shell, navigation, header, and footer |
| `_layouts/post.html` | Blog post presentation |
| `_plugins/single_dollar_math.rb` | Makes Kramdown parse `$...$` as inline math before MathJax renders it |
| `_sass/_general.scss` | Site colors, typography, layout, and responsive styles |
| `assets/styles/main.scss` | Sass entry point; normally does not need editing |
| `_config.yml` | Site title, contact details, URL, defaults, and Jekyll configuration |
| `_site/` | Generated output; never edit this directory |

The `student-distribution-tool/` directory is a separate static application. It is not part of the normal page, blog, or styling workflow described below.

## Edit an existing page

Most site content is Markdown in `_pages/`. For example:

- Edit `_pages/index.md` for the home page.
- Edit `_pages/cv.md` for the CV.
- Edit `_pages/contact.md` for contact information shown in the page body.
- Edit `_pages/publications.md` and `_pages/notes.md` as those sections grow.

Each page starts with YAML front matter:

```yaml
---
layout: default
title: Notes
permalink: /notes
description: Longer notes and expository writing in progress.
---
```

The fields have the following roles:

- `layout` selects the shared HTML layout.
- `title` is used in the browser title.
- `permalink` fixes the public URL. Avoid changing an existing permalink unless you intend to break or redirect old links.
- `description` supplies the page's HTML meta description.

Write the page below the closing `---` using Markdown. Ordinary HTML and Liquid template expressions can also be used when Markdown is not sufficient.

## Edit global information

Change `_config.yml` when updating information used across the site, including:

```yaml
title: Metin Ersin Arıcan
email: metin.ersin.arican@gmail.com
tagline: Mathematics graduate student working in logic, model theory, and formalization.
twitter_username: ersin_ar
github_username: metinersin
```

Templates access these values through expressions such as `{{ site.email }}`. Restart `make preview` after changing `_config.yml`, because Jekyll does not automatically reload configuration changes.

The home page also has `hero_kicker` and `hero_summary` fields in `_pages/index.md`. These control the large introductory card at the top of the home page.

## Add a blog post

Create a Markdown file in `_posts/` using this filename format:

```text
YYYY-MM-DD-short-title.md
```

Start it with front matter like this:

```yaml
---
layout: post
title: "Post title"
date: 2026-08-04 12:00 +0300
categories: mathematics model-theory
---

Write the post here.
```

Posts are automatically listed on the Blog page, newest first. Their public URLs are generated from the categories and title according to the post permalink rule in `_config.yml`.

Mathematical notation can be written with the standard LaTeX-style delimiters because the shared layout loads MathJax. Use single dollar signs for inline mathematics and double dollar signs on separate lines for displayed mathematics:

```text
Inline mathematics: $x^2 + y^2$.

Displayed mathematics:

$$
\forall x\, \exists y\, \varphi(x,y)
$$
```

Escape a literal dollar sign with a backslash, as in `\$10`.

## Add or edit a project

The Projects page reads its cards from `_data/projects.yml`. Add another item using the existing structure:

```yaml
- name: Project name
  summary: >
    A concise explanation of the project and its purpose.
  stack:
    - Technology one
    - Technology two
  links:
    - label: GitHub
      url: https://github.com/example/project
    - label: Live site
      url: https://example.com
  notes: Optional additional information.
```

The card markup lives in `_pages/projects.md`, but normal project updates should only require editing `_data/projects.yml`. YAML indentation matters: use spaces, keep sibling fields aligned, and do not use tabs.

## Add a main page

1. Create a Markdown file under `_pages/` with `layout`, `title`, `permalink`, and `description` front matter.
2. Add the page content below the front matter.
3. Add a navigation link in `_layouts/default.html` if the page belongs in the main menu.
4. Add the page to `_pages/map.md` if it belongs in the site map.
5. Run `make preview` and check the page on both a wide and narrow browser window.

Navigation is written manually in `_layouts/default.html`; creating a page does not automatically add it to the menu. Follow the existing `relative_url` and active-page patterns when adding a link:

```liquid
<a href="{{ '/example' | relative_url }}"{% if page.url == '/example' %} class="is-active"{% endif %}>Example</a>
```

## Change the design

Edit `_sass/_general.scss` for the main site's appearance. It contains:

- Font families and color variables near the top.
- Shared header, navigation, page card, and footer styles.
- Project and blog card styles.
- Responsive rules near the bottom.

Jekyll compiles this file through `assets/styles/main.scss` into `/assets/styles/main.css`. Edit the Sass source, not the generated CSS in `_site/`.

The shared page structure is in `_layouts/default.html`. Changes there affect almost every page, so check the home page, an ordinary page, and a blog post after editing it.

## Links and URLs

Use `{% raw %}{{ '/path' | relative_url }}{% endraw %}` in layouts and Liquid templates for internal links. In Markdown content, existing root-relative links such as `/cv/` are also used throughout the site.

Keep existing trailing-slash behavior when linking to a page. In particular, the CV uses `/cv/`, while several other pages use extensionless URLs such as `/projects` and `/blog`.

## Publishing checklist

1. Run `make preview` and inspect the changed pages.
2. Check internal and external links.
3. Check the layout at desktop and mobile widths.
4. Run `make build` and fix any reported errors.
5. Review `git diff` to ensure only intended source files changed.
6. Commit and push the changes to the publishing branch.

The workflow in `.github/workflows/pages.yml` builds and publishes the site through GitHub Actions. The custom build is required because GitHub Pages' safe-mode Jekyll builder does not load the local single-dollar math plugin. In the repository's Pages settings, select **GitHub Actions** as the deployment source. `_site/` is ignored by Git, so normal commits should contain source changes rather than generated output.

## Troubleshooting

If a bare `bundle exec jekyll ...` command fails, reproduce the issue with `make build` or `./script/build` before treating it as a project problem. macOS may select its old system Ruby, while this repository is pinned to Ruby 3.4.

Useful commands:

```sh
make build            # Production build
make preview          # Local server at 127.0.0.1:4000
make doctor           # Full toolchain and build check
./script/bundle check # Check installed gems using the repository toolchain
```

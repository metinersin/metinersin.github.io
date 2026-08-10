# Agent Notes

The authoritative local build check for this repository is `make build` or `./script/build`.

The site uses Quarto and requires Quarto 1.10 or newer. Do not treat a bare Pandoc conversion as a project build: Quarto supplies the website navigation, listings, search index, feeds, and resource copying.

Use these commands:

- `make build` or `./script/build` for a production render
- `make preview` or `./script/preview` for local preview
- `make doctor` or `./script/doctor` for a Quarto check and production render

The generated `_site/` and `.quarto/` directories are disposable build output. The standalone `student-distribution-tool/` directory must remain available at `/student-distribution-tool/` after every build.

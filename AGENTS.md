# Agent Notes

The authoritative local build check for this repo is `make build` or `./script/build`.

Do not treat bare `bundle exec jekyll ...` failures as project build failures unless you have first reproduced the issue with the wrapper scripts. The repo is pinned to Ruby `3.4` in `.ruby-version`, and the wrapper scripts select a compatible Ruby plus the Bundler version from `Gemfile.lock`.

Use these commands:

- `make build` or `./script/build` for a production build
- `make preview` or `./script/preview` for local preview
- `make doctor` or `./script/doctor` for a full toolchain and build check
- `./script/bundle ...` for Bundler commands in this repo

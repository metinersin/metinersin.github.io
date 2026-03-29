# metinersin.github.io

## Local development

Use the repo wrappers instead of bare `bundle exec ...`. This site is pinned to Ruby `3.4` in `.ruby-version`, while macOS still ships Ruby `2.6`, so raw Bundler commands from an unconfigured shell can look broken even when the site build is healthy.

- `make build` or `./script/build` builds the site into `_site/`
- `make preview` or `./script/preview` serves the site at `http://127.0.0.1:4000`
- `make doctor` or `./script/doctor` verifies the Ruby/Jekyll toolchain and runs a full build
- `./script/bundle ...` is the supported way to run Bundler commands for this repo

The wrapper scripts automatically:

- choose a compatible Ruby
- use the Bundler version pinned in `Gemfile.lock`
- install missing gems into a repo-specific bundle path when needed

If plain `bundle exec jekyll ...` fails under the system Ruby, treat that as a shell setup mismatch, not as a site build failure.

# go-loader-github

[![npm](https://img.shields.io/npm/v/go-loader-github.svg?style=flat-square)](https://www.npmjs.com/package/go-loader-github)
[![Travis](https://img.shields.io/travis/gocli/go-loader-github.svg?style=flat-square)](https://travis-ci.org/gocli/go-loader-github)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-loader-github.svg?style=flat-square)](https://coveralls.io/github/gocli/go-loader-github)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-loader-github/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-loader-github)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-loader-github)

[Go](https://www.npmjs.com/package/go) loader for Github

## Usage

```bash
$ npm install --global go go-loader-github
$ go github gocli/boilerplate-example
```

## Options

```bash
$ go github <source>[:reference] <destination> [options]
```

- `source` — valid source in a format `username/repository`
- `reference` — git reference to checkout after installation (has priority over `options.checkout`)
- `destination` — folder path to put loaded files (destination folder will be created if it doesn't exist)
- `options`:
  - `--no-install` — do not install boilerplate after loading
  - `--keep-git` (`-k`) — do not remove `.git/` directory after loading repository
  - `--checkout <string>` — git reference (tag, branch, etc) to checkout after repository is loaded
  - `--depth <number>` — truncate history by number of commits
  - `--git <string>` — path to Git binary

## License

MIT © [Stanislav Termosa](https://github.com/termosa)


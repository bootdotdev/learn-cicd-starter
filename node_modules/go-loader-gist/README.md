# go-loader-gist

[![npm](https://img.shields.io/npm/v/go-loader-gist.svg?style=flat-square)](https://www.npmjs.com/package/go-loader-gist)
[![Travis](https://img.shields.io/travis/gocli/go-loader-gist.svg?style=flat-square)](https://travis-ci.org/gocli/go-loader-gist)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-loader-gist.svg?style=flat-square)](https://coveralls.io/github/gocli/go-loader-gist)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-loader-gist/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-loader-gist)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-loader-gist)

[Go](https://www.npmjs.com/package/go) loader for Gist

## Usage

```bash
$ npm install --global go go-loader-gist
$ go gist <gist_hash>
$ go gist <gist_hash>/<version_sha>
```

## Options

```bash
$ go gist <source> <destination> [options]
```

- `source` — gist hash and version optionally separated by slash
- `destination` — folder path to put loaded files (destination folder will be created if it doesn't exist)
- `options`:
  - `--no-install` — do not install boilerplate after loading

## License

MIT © Stanislav Termosa <termosa.stanislav@gmail.com> (http://me.st)


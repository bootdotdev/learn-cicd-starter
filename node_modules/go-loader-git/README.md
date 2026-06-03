# go-loader-git

[![npm](https://img.shields.io/npm/v/go-loader-git.svg?style=flat-square)](https://www.npmjs.com/package/go-loader-git)
[![Travis](https://img.shields.io/travis/gocli/go-loader-git.svg?style=flat-square)](https://travis-ci.org/gocli/go-loader-git)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-loader-git.svg?style=flat-square)](https://coveralls.io/github/gocli/go-loader-git)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-loader-git/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-loader-git)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-loader-git)

[Go](https://www.npmjs.com/package/go) loader for git repositories

## Usage

```bash
$ npm install --global go go-loader-git
$ go git git@github.com:gocli/boilerplate-example.git
```

### Shortcut

[Go CLI](https://www.npmjs.com/package/go-cli) has shortcut for this loader, so you don't need to write `git`:

```bash
$ go git@github.com:gocli/boilerplate-example.git
```

## Options

```bash
$ go git <repository> [destination] [options]
```

- `repository` — valid git link to a repository
- `destination` — folder path to put loaded files (destination folder will be created if it doesn't exist)
- `options`:
  - `--no-install` — do not install boilerplate after loading
  - `--keep-git` (`-k`) — do not remove `.git/` directory after loading repository
  - `--checkout <string>` — git reference (tag, branch, etc) to checkout after repository is loaded
  - `--depth <number>` — truncate history by number of commits
  - `--git <string>` — path to Git binary

## Examples

```bash
# install boilerplate from Bitbucket to ./sources/new-project
$ go git git@bitbucket.org:repository/path.git sources/new-project

# install boilerplate from GitHub to ./path
$ go git https://github.com/repository/path.git
```

## License

MIT © [Stanislav Termosa](https://github.com/termosa)


# go

[![npm](https://img.shields.io/npm/v/go.svg?style=flat-square)](https://www.npmjs.com/package/go)
[![Travis](https://img.shields.io/travis/gocli/go.svg?style=flat-square)](https://travis-ci.org/gocli/go)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go.svg?style=flat-square)](https://coveralls.io/github/gocli/go)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go)
[![Waffle](https://badge.waffle.io/gocli/go.svg?columns=In%20progress,Backlog&style=flat-square)](https://waffle.io/gocli/go)

Go is the toolset to manage boilerplates with less effort.

## Usage

Go can be used in 2 ways:

### Load and install boilerplate

```bash
$ npm install --global go
$ go git git@github.com:gocli/boilerplate-example.git
```

To create and use your own boilerplates, refer to [documentation](http://gocli.io) or check the list of [community driven boilerplates](http://gocli.io/boilerplates).

### Run local commands

```bash
$ cd project/with/gofile/
$ go run some command
```

This will call the command registered in **gofile.js**.
Take a time to read how to [create your own gofile.js](http://gocli.io/#gofile).

#### Interactive menu

You can also execute **go** with no arguments and that will call an interactive menu with the list of all available commands:

```bash
$ go
[GO] Choose command:
❯ build
  deploy
  generate
  install
```

## Go Lang

It works well with [Go programming language](https://golang.org). In case you have any issues read [troubleshooting page](http://gocli.io/golang).

## License

MIT © [Stanislav Termosa](https://github.com/termosa)

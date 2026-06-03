# go-plugin-fs

[![npm](https://img.shields.io/npm/v/go-plugin-fs.svg?style=flat-square)](https://www.npmjs.com/package/go-plugin-fs)
[![Travis](https://img.shields.io/travis/gocli/go-plugin-fs.svg?style=flat-square)](https://travis-ci.org/gocli/go-plugin-fs)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-plugin-fs.svg?style=flat-square)](https://coveralls.io/github/gocli/go-plugin-fs)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-plugin-fs/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-plugin-fs)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-plugin-fs)

[Go](https://www.npmjs.com/package/go) plugin to work with file system.

## Table of Contents

- [go-plugin-fs](#go-plugin-fs)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
  - [API](#api)
    - [Methods](#methods)
      - [copy](#copy)
      - [move](#move)
      - [remove](#remove)
      - [writeFile](#writefile)
      - [readFile](#readfile)
      - [createDir](#createdir)
  - [Examples](#examples)
    - [Basic usage](#basic-usage)
    - [Read and write file](#read-and-write-file)
  - [License](#license)

## Usage

```bash
$ npm install --save-dev go go-plugin-fs
```

```js
import go from 'go'
import { FsPlugin } from 'go-plugin-fs'

go.use(FsPlugin)

go.copy('./path/to/source/file', './destination/path')
```

## API

### Methods

#### copy

```
go.copy( source, target [ , options, callback ]): Promise<void>
go.copySync( source, target [ , options ]): void
```

Copies file or directory to the target destination (it creates missing directories automatically).
Read more about fs-extra [copy](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/copy.md) and [copySync](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/copy-sync.md).

#### move

```
go.move( source, target [ , options, callback ]): Promive<void>
go.moveSync( source, target [ , options ]): void
```

Moves file or directory to the target destination (it creates missing directories automatically).
Read more about fs-extra [move](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/move.md) and [moveSync](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/move-sync.md).

#### remove

```
go.remove( path [ , callback ]): Promise<void>
go.removeSync( path ): void
```

Removes file or directory.
Read more about fs-extra [remove](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/remove.md) and [removeSync](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/remove-sync.md).

#### writeFile

```
go.writeFile( path, data [ , options, callback ]): Promise<void>
go.writeFileSync( path, data [ , options ]): void
```

Creates or rewrites the file with given content.
Read more about fs-extra [outputFile](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/outputFile.md) and [outputFileSync](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/outputFile-sync.md).

#### readFile

```
go.readFile( path [ , options, callback ]): Promise<void>
go.readFileSync( path [ , options ]): void
```

Reads the content from the given file.
Read more about NodeJS [readFile](https://nodejs.org/api/fs.html#fs_fs_readfile_path_options_callback) and [readFileSync](https://nodejs.org/api/fs.html#fs_fs_readfilesync_path_options).

#### createDir

```
go.createDir( path, data [ , options, callback ]): Promise<void>
go.createDirSync( path, data [ , options ]): void
```

Creates the directory if it doesn't exist (it also creates missing directories in the path automatically).
Read more about fs-extra [ensureDir](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/ensureDir.md) and [ensureDirSync](https://github.com/jprichardson/node-fs-extra/blob/5.0.0/docs/ensureDir-sync.md).

## Examples

### Basic usage

```js
const newComponentName = 'new-component'
go.copy('./templates/component.js', `./src/components/${newComponentName}.js`)
```

### Read and write file

```js
const contributorsPath = './CONTRIBUTORS.md'
const newContributor = 'Chuck Norris'

go.readFile(contributorsPath)
  .then((content) => `${content}\n - ${newContributor}`)
  .then((content) => go.writeFile(contributorsPath, content))
```

## License

MIT © [Stanislav Termosa](https://github.com/termosa)

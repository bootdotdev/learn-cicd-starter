# go-plugin-templates

[![npm](https://img.shields.io/npm/v/go-plugin-templates.svg?style=flat-square)](https://www.npmjs.com/package/go-plugin-templates)
[![Travis](https://img.shields.io/travis/gocli/go-plugin-templates.svg?style=flat-square)](https://travis-ci.org/gocli/go-plugin-templates)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-plugin-templates.svg?style=flat-square)](https://coveralls.io/github/gocli/go-plugin-templates)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-plugin-templates/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-plugin-templates)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-plugin-templates)

[Go](https://www.npmjs.com/package/go) plugin to use templates.

> This plugin is made on top of [Embedded JavaScript templates](https://www.npmjs.com/package/ejs) and [globby](https://www.npmjs.com/package/globby). Thanks [@mde](https://www.npmjs.com/~mde), [@schnittstabil](https://www.npmjs.com/~schnittstabil), [@sindresorhus](https://www.npmjs.com/~sindresorhus) and [@ult_combo](https://www.npmjs.com/~ult_combo) for it!

## Table of Contents

- [go-plugin-templates](#go-plugin-templates)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Installation](#installation)
    - [Quick Start](#quick-start)
  - [API](#api)
    - [Methods](#methods)
      - [createTemplate](#createtemplate)
      - [loadTemplates](#loadtemplates)
      - [processTemplates](#processtemplates)
    - [Templates Methods](#templates-methods)
      - [render](#render)
      - [write](#write)
      - [getSource](#getsource)
    - [Template Syntax](#template-syntax)
  - [License](#license)

## Usage

### Installation

```bash
$ npm install --save-dev go go-plugin-templates
```

```js
import go from 'go'
import { TemplatesPlugin } from 'go-plugin-templates'
go.use(TemplatesPlugin)
```

### Quick Start

Templates Plugin helps you to you template files in your project.
So you can generate your code out of template files.
For example, you may want to change the app name in the readme file:

```js
const appName = 'New App'
go.processTemplates({ appName }, 'README.md')
```

**README.md** file:
```md
# <%= appName %>

more content…
```

Or you can create few new modules in your project:

```js
const moduleTemplate = go.loadTemplates.sync('.templates/module.js')
moduleTemplate.write({ name: 'authentication' }, './app/modules/authentication.js')
moduleTemplate.write({ name: 'authorization' }, './app/modules/authorization.js')
```

You can also create templates out of string:

```js
go.createTemplate(`# Contributors
<% contributors.forEach(contrib => { %>
<%= contrib.name %> <<%= contrib.email %>> (<%= contrib.link %>)
<% }) %>`)
```

Or you can create the whole project from the directory:

```js
go.processTemplates(data, './microservice-project-template', 'microservices/new-one/')
```

It is possible to change the name of files before saving them:

```js
go.processTemplates(data, 'templates/**', ({ ext, base }) => `assets/<%= ext %>/<%= base %>`)
```

## API

### Methods

#### createTemplate

```
crateTemplate( template [ , options ] ): Template
```

Creates a [template](#templates-methods) from string.

- `template` {string} - text with ejs placeholders
- `options` {object} - all ejs options + `filename` and `resolve` properties
  - `filename` {string} - a path to the file (used in getSource() and to write rendered template)
  - `resolve` {string|function} - will be used for `write` if it is called without `resolve` argument
  - default ejs option `escape` is replaced with `str => str` so it won't affect templates

#### loadTemplates

```
loadTemplates( [ search, options ] ): Promise<Template[]>
loadTemplates.sync( [ search, options ] ): Template[]
```

Creates a [list of templates](#templates-methods) out of matched files.

- `search` {string|array|object} - globby options to search files
  - string, becomes a pattern to search
  - array, becomes patterns to search
  - object, is globby options object
  - for each of above cases there are several default options (redefined from globby defaults) will be assigned:
    - `cwd: process.cwd()`
    - `dot: true`
    - `ignore: ['.git', 'node_modules']`
    - `pattern: '**'`
- `options` {object} - this will be given as it is (but `filename` will be changed) to `createTemplate` as options

#### processTemplates

```
processTemplates( context [ , search, options ] ): Promise<void>
processTemplates.sync( context [ , search, options ] ): void
```

Creates a [list  of templates](#templates-methods) out of matched files and writes them.

- `search` {string|array|object} - as it is goes to `loadTemplates`
- `context` {object} - as it is goes to `render`
- `options` {object} - this will be given as it is (but `filename` will be changed) to `createTemplate` as options

### Templates Methods

There is a Templates List (returned by [`loadTemplates`](#loadtemplates)) and a Template (that is a member of Templates list and a return value of [`createTemplate`](#createtemplate)).

#### render

```
template.render( [ context ] ): string
templates.render( [ context ] ): string[]
```

Renders templates with a given context.

- `context` {object} - a scope for ejs template

#### write

```
template.write( [ context, resolve ] ): Promise<void>
template.write.sync( [ context, resolve ] ): void
templates.write( [ context, resolve ] ): Promise<void>
templates.write.sync( [ context, resolve ] ): void
```

Renders templates with a given context and write them to files.

- `context` {object} - as it is goes to `render`
- `resolve` {string|function} - a path to save the file
  - string, if it ends with directory separator (/) will put files in that directory with their names from `filename`, otherwise it will be an exact path to save file; it also can contain ejs placeholders to use file meta information
  - function, receives meta information about the file and should return a string that is exact path to save the file

#### getSource

```
template.getSource(): string
```

Returns template source file name.

### Template Syntax

[Embedded JavaScript templates](https://www.npmjs.com/package/ejs) library is used to provide to you template features. Nothing is changed so you can read more about its features on [ejs page](https://www.npmjs.com/package/ejs).

## License

MIT © [Stanislav Termosa](https://github.com/termosa)

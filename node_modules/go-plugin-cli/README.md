# go-plugin-cli

[![npm](https://img.shields.io/npm/v/go-plugin-cli.svg?style=flat-square)](https://www.npmjs.com/package/go-plugin-cli)
[![Travis](https://img.shields.io/travis/gocli/go-plugin-cli.svg?style=flat-square)](https://travis-ci.org/gocli/go-plugin-cli)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-plugin-cli.svg?style=flat-square)](https://coveralls.io/github/gocli/go-plugin-cli)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-plugin-cli/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-plugin-cli)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-plugin-cli)

[Go](https://www.npmjs.com/package/go) plugin to create and [execute commmands](https://www.npmjs.com/package/go-cli).

> This plugin is made on top of [Liftoff](https://www.npmjs.com/package/liftoff). Thanks [@jonschlinkert](https://www.npmjs.com/~jonschlinkert), [@phated](https://www.npmjs.com/~phated), [tkellen](https://www.npmjs.com/~tkellen) and [tusbar](https://www.npmjs.com/~tusbar) for it!

## Table of Contents

- [go-plugin-cli](#go-plugin-cli)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Installation](#installation)
    - [Quick Start](#quick-start)
  - [Api](#api)
    - [Methods](#methods)
      - [registerCommand](#registercommand)
      - [matchCommand](#matchcommand)
      - [executeCommand](#executecommand)
      - [getCommands](#getcommands)
    - [CLI](#cli)
    - [Command](#command)
      - [name](#name)
      - [callback](#callback)
      - [commands](#commands)
      - [description](#description)
      - [title](#title)
      - [prefix](#prefix)
      - [when](#when)
      - [options](#options)
    - [Parsed Command](#parsed-command)
    - [Parsing Command Options](#parsing-command-options)
  - [Examples](#examples)
  - [License](#license)

## Usage

### Installation

```bash
$ npm install --save-dev go go-plugin-cli
```

```js
import go from 'go'
import { CliPlugin } from 'go-plugin-cli'
go.use(CliPlugin)
```

### Quick Start

Cli Plugin helps you to create command-line interface for your boilerplate and commands.
You can easily create interactive menus for your app when using it in pair with [Go CLI](https://npmjs.com/package/go-cli).
For example, you may want to provide `install` command in CLI:

```js
// gofile.js in root directory of your application
import go from 'go'
import { CliPlugin } from 'go-plugin-cli'
go.use(CliPlugin)

go.registerCommand('greet', async () => {
  console.log('Welcome!')
})
```

```bash
$ go greet
Welcome!
```

## Api

### Methods

#### registerCommand

```
go.registerCommand( commands [ , callback ] ): void
```

- `commands` {string|object|array} — can be a string that will result in a name of a command, an object with [command options](#command) or an array of mixed string and objects
- `callback` {function} — becomes a callback for a command when `commands` is a string

Registers new command to the list.

#### matchCommand

```
go.matchCommand( commandString ): Command
```

- `commandString` {string} — a string with the name of command and flags

Find a registered command.

#### executeCommand

```
go.executeCommand( commandString ): Promise<any>
```

- `commandString` {string} — a string with the name of command and flags

Find and execute registered command.

#### getCommands

```
go.getCommands(): Command[]
```

Returns a RAW list of registered commands.

### CLI

```bash
$ go # to run interactive menu
$ go command with flags # to run the registered command
```

### Command

Command is an object with options. Here is the list of possible options:

#### name

- Required
- Valid types: `string`

The name of the command that will be used to trigger it.

#### callback

- Required (if [`commands`](#commands) are not provided)
- Valid types: `function`
- Function arguments: `object` ([parsed command](#parsed-command))

The callback function will be called when command is triggered.

#### commands

- Required (if [`callback`](#callback) is not provided)
- Valid types: `array` (a list of [commands](#command))

Nested commands can be triggered by using their name after the name of parent command, or from [interactive menu](https://github.com/gocli/go#interactive-menu).

#### description

- Valid types: `string`

The description of the command that will be shown in the interactive menu.

#### title

- Valid types: `string`
- Default value: `"Choose command:"`

The title will be shown in interactive menu for nested commands.

#### prefix

- Valid types: `string`
- Default value: `"GO"`

The prefix will be shown in interactive menu for nested commands.

#### when

- Valid types: `string|array|object|function`
- Function arguments: `object` ([parsed command](#parsed-command))

Adds additional check when matching command.
This lets you use the same command name and trigger different commands depending on flags or environment.

If `when` is specified as a `string` it will match the command only if specified flag has truthy value.
`when` can also be specified as an array of `string`'s.
Then the precense of each mentioned flag will be validated.
To check the specific value of the flag `when` can be given as an object in a format `{ flagName: flagValue }`.

For more control `function` can be used as `when` option.
It should return either truthy or falsy value and that will determine if command is matching or not.

#### options

- Valid types: `object`

The configuration object for parsing command.
When used in nested command it iherits options from parent commands.
Read [parsing command options](#parsing-command-options) section to learn more about it.

### Parsed Command

Command callbacks receive parsed CLI command as an argument. The structure of an object:

- `args` {object} — parsed command
  - `_` {array} — the list of command partials (strings)
  - `[flag name]` {boolean|string} — values of each given flag
  - `--` {array} — the list of strings given after `--` sign

### Parsing Command Options

There is an option to configure how command will be parsed.
This is an object that can be written in 2 ways: `{ flagName: type }` or `{ flagName: options }`

List of options:

- `type` {Boolean|String} — defines how flag should be parsed
- `alias` {string|array} — alias string or an array of alias strings
- `default` {any} — default value when flag is not used

## Examples



## License

MIT © [Stanislav Termosa](https://github.com/termosa)

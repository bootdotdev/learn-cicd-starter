# go-plugin-quiz

[![npm](https://img.shields.io/npm/v/go-plugin-quiz.svg?style=flat-square)](https://www.npmjs.com/package/go-plugin-quiz)
[![Travis](https://img.shields.io/travis/gocli/go-plugin-quiz.svg?style=flat-square)](https://travis-ci.org/gocli/go-plugin-quiz)
[![Coveralls](https://img.shields.io/coveralls/github/gocli/go-plugin-quiz.svg?style=flat-square)](https://coveralls.io/github/gocli/go-plugin-quiz)
[![Vulnerabilities](https://snyk.io/test/github/gocli/go-plugin-quiz/badge.svg?style=flat-square)](https://snyk.io/test/github/gocli/go-plugin-quiz)
[![js-standard-style](https://img.shields.io/badge/code%20style-standard-green.svg?style=flat-square)](https://github.com/gocli/go-plugin-quiz)

![go-plugin-quiz example](https://raw.githubusercontent.com/gocli/go-plugin-quiz/master/docs/example.gif)

[Go](https://www.npmjs.com/package/go) plugin to communicate with user using shell prompt.

> This plugin is made on top of [Inquirer](https://www.npmjs.com/package/inquirer). Thanks [@sboudrias](https://www.npmjs.com/~sboudrias) and [@mischah](https://www.npmjs.com/~mischah) for it!

## Table of Contents

- [go-plugin-quiz](#go-plugin-quiz)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Installation](#installation)
    - [Quick Start](#quick-start)
  - [API](#api)
    - [Methods](#methods)
      - [confirm](#confirm)
      - [ask](#ask)
      - [ask.separator](#askseparator)
      - [registerQuestion](#registerquestion)
    - [Question Object](#question-object)
      - [type](#type)
      - [name](#name)
      - [message](#message)
      - [default](#default)
      - [choices](#choices)
      - [validate](#validate)
      - [filter](#filter)
      - [transformer](#transformer)
      - [when](#when)
      - [pageSize](#pagesize)
      - [prefix](#prefix)
      - [suffix](#suffix)
      - [mask](#mask)
      - [multiple](#multiple)
      - [source](#source)
      - [suggestOnly](#suggestonly)
    - [Session](#session)
    - [Result](#result)
    - [Question Types](#question-types)
      - [Available Types](#available-types)
        - [Input](#input)
        - [Password](#password)
        - [Confirm](#confirm)
        - [List](#list)
        - [Raw List](#raw-list)
        - [Checkbox](#checkbox)
        - [Autocomplete](#autocomplete)
        - [Editor](#editor)
        - [Expand](#expand)
      - [Duck Typing](#duck-typing)
      - [More Types](#more-types)
  - [Examples](#examples)
    - [Ask for the basic text input](#ask-for-the-basic-text-input)
    - [Ask a question with options](#ask-a-question-with-options)
    - [Question as an object](#question-as-an-object)
    - [Ask a sequence of questions](#ask-a-sequence-of-questions)
    - [Default options for multiple questions](#default-options-for-multiple-questions)
    - [Named answers](#named-answers)
    - [Conditional questions](#conditional-questions)
    - [Input validation](#input-validation)
    - [Answer transformation](#answer-transformation)
  - [License](#license)

## Usage

### Installation

```bash
$ npm install --save-dev go go-plugin-quiz
```

```js
import go from 'go'
import { QuizPlugin } from 'go-plugin-quiz'
go.use(QuizPlugin)
```

### Quick Start

Quiz Plugin helps you to communicate with your users using shell prompts.
It let you ask a question or a sequence of questions using simple API.
For example, you may want to ask a user to enter a custom string:

```js
go.ask('What is your favorite color?')
  .then((color) => {
    console.log(`We've changed skin of your site to ${color} one`)
  })
```

Or you can predefine a list of available options:

```js
go.ask({
  message: 'What is your favorite color?',
  choices: [ 'Red', 'Blue', 'Green' ]
}).then((color) => {
  console.log(`We've changed skin of your site to ${color} one`)
})
```

There are different types of prompts:

```js
go.ask({
  type: 'confirm',
  message: 'Do you want to deploy code to production?'
}).then((confirmed) => {
  console.log(confirmed ? 'Good luck!' : 'Let\'s do more testing!')
})
```

And then you can chain them:

```js
go.ask([
  { name: 'server',
    message: 'Where do you want to deploy?',
    choices: [ 'test server', 'stage', 'production' ] },
  { name: 'continue',
    type: 'confirm',
    message: 'You are about to deploy it. Continue?' }
]).then((answers) => {
  if (answers.continue) {
    console.log(`Deploying to ${answers.server}`)
  } else {
    console.log('Let\'s do more testing!')
  }
})
```

## API

### Methods

#### confirm

```
go.confirm( message [ , default ] ): Promise<Answer>
```

This is a shortcut for `go.ask( { type: 'confirm', message, default } )`

#### ask

```
go.ask( questions [ , defaults ] ): Promise<Answer | Answers[]>
```

Asks a user for input in a shell.

- `questions` {string|object|array} — can be a [Question Object](#question-options), a string (it will resolve to `message` property of a question), or an array with mix of Question Objects and strings.
- `defaults` {object} — is an object that defined default properties for each question in a list.

Every call of the `ask` is creating a new [session](#session) that can be used to change `ask` behavior during execution.

#### ask.separator

```
go.ask.separator( [ message ] ): ChoicesSeparator
```

Generate a special object that can be used in [choices](#choices) to create an inactive line in the list.

- `message` {stirng} — text to be used in a separator

#### registerQuestion

```
go.registerQuestion( type, prompt ): void
```

Register a new question type.

- `type` {string} — name of a new question type
- `prompt` {object} — [InquirerPrompt](https://www.npmjs.com/package/inquirer#plugins) instance

For more details, read chapter [More Types](#more-types)

### Question Object

Every question is an object that may contain one or multiple of options listed below.

#### type

- Valid types: `string`
- Possible values: `"input"`, `"confirm"`, `"list"`, `"rawlist"`, `"expand"`, `"checkbox"`, `"password"`, `"editor"`, `"autocomplete"`, and [more](#registerquestion)
- Default value: `"input"`
- Supported questions: ALL

The [type](#question-types) of the question.

#### name

- Valid types: `string`
- Supported questions: ALL

The name that will be used to store answer in the **answers** object.

#### message

- Required
- Valid types: `string | function`
- Function arguments: `answers`
- Supported questions: ALL

The question to print.
If defined as a function, the first parameter will be the **answers** object of the current [session](#session).

#### default

- Valid types: `string | number | array | function`
- Function arguments: `answers`
- Supported questions: [Input](#input), [Password](#password), [Confirm](#confirm-1), [List](#list), [Raw List](#raw-list), [Checkbox](#checkbox), [Expand](#expand), [Editor](#editor)

Default value(s) to use if nothing is entered, or a function that returns the default value(s).
If defined as a function, the first parameter will be the **answers** object of the current [session](#session).

#### choices

- Valid types: `array | function`
- Function arguments: `answers`
- Supported questions: [List](#list), [Raw List](#raw-list), [Checkbox](#checkbox), [Expand](#expand)

Choices is an array or a function returning a choices array.
If defined as a function, the first parameter will be the **answers** object of the current [session](#session).
Array values can be simple `strings`, or `objects` containing a **name** (to display in list), a **value** (to save in the **answers** object), a **short** (to display after selection) properties, and a **checked** (to make it selected when using with [Checkbox](#checkbox)).
The choices array can also contain a [Separator](#askseparator).

#### validate

- Valid types: `function`
- Function arguments: `input, answers`
- Supported questions: [Input](#input), [Password](#password), [Checkbox](#checkbox), [Editor](#editor), [Autocomplete#suggestOnly](#suggestonly)

Receive the user **input** and **answers** object.
Should return `true` if the value is valid, and an error message (`string`) otherwise.
If `false` is returned, a default error message is provided.

#### filter

- Valid types: `function`
- Function arguments: `input, answers`
- Supported questions: [Input](#input), [Password](#password), [List](#list), [Raw List](#raw-list), [Checkbox](#checkbox), [Autocomplete](#autocomplete), [Editor](#editor)

Receive the user **input** and **answers** object.
Return the filtered value that will be stored to the **answers** object.

#### transformer

- Valid types: `function`
- Function arguments: `input, answers`
- Supported questions: [Input](#input)

Receive the user **input** and **answers** object.
Return the transformed value to be displayed to the user.
The transformation only impacts what is shown while editing.
It does not impact the **answers** object.

#### when

- Valid types: `boolean | function`
- Function arguments: `answers`
- Supported questions: ALL

Receive the current user **answers** object and should return `true` or `false` depending on whether or not this question should be asked.
The value can also be a simple boolean.

#### pageSize

- Valid types: `number`
- Supported questions: [List](#list), [Raw List](#raw-list), [Expand](#expand), [Checkbox](#checkbox), [Autocomplete](#autocomplete)

Change the number of lines that will be rendered.

#### prefix

- Valid types: `string`
- Supported questions: ALL

Change the default prefix message.

#### suffix

- Valid types: `string`
- Supported questions: ALL

Change the default suffix message.

#### mask

- Valid types: `string`
- Supported questions: [Password](#password)

Replace every entered character with the given string.

#### multiple

- Valid types: `boolean`
- Default value: `false`
- Supported questions: [Checkbox](#checkbox)

If **type** is not declared, but **choices** list is defined and **multiple** is truthy, the question type is assigned to `checkbox`.

#### source

- Valid types: `array | function`
- Function arguments: `input, answers`
- Supported questions: [Autocomplete](#autocomplete)

If defined as a function, the first parameter will be the user **input** and the second is the **answers** object of the current [session](#session).
`source` function must return a promise.
If `source` defined as an `array` it will be wrapped with a function that filters list by case-insensitive partial match.
For the first time before the user types anything `source` will be called with `null` as the value.
If a new search is triggered by user input it maintains the correct order, meaning that if the first call completes after the second starts, the results of the first call are never displayed.

#### suggestOnly

- Valid types: `boolean`
- Default value: `false`
- Supported questions: [Autocomplete](#autocomplete)

Setting it to true turns the input into a normal text input.
Meaning that pressing enter selects whatever value you currently have.
And pressing tab autocompletes the currently selected value in the list.
This way you can accept manual input instead of forcing a selection from the list.

### Session

The session stores all user answers to return them as a result of execution and make them available during runtime as an **answers** argument of questions methods like [`when`](#when), [`validate`](#validate) and [others](#question-options).

The **answers** object is of a type `array` and stores answers in the same order as questions were organized.
As well, **answers** object has a property named `_` (underscore) that contains a hash object with answers for questions that were defined with **name** attribute that is used as a `key` in that object.
The same list of keys is assigned to **answers** object.
It makes using [`ask`](#ask) together with [destructuring object assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment) nicer.

A new session is created for every [`ask`](#ask) call.

### Result

[`go.ask`](#ask) and [`go.confirm`](#confirm) return promises as the result.
It resolves either with what user choose or entered or with an **answers** object created in [session](#session) when `go.ask` was called with an array of questions.

You may use [Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise), [async/await](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await) and [destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment) features to retrieve answer(s):

```js
// Retrieving an answer for a single question

go.ask('What is your name?')
  .then((name) => { /* … */ })
// or
(async () => {
  const name = await go.ask('What is your name?')
})()
```

```js
// Retrieving answers for multiple questions

const answers = await go.ask([
  { name: 'name', 'How to name your project?' },
  { name: 'description', 'Give it a short description:' }
])
// or
const [ name, description ] = await go.ask([
  { name: 'name', 'How to name your project?' },
  { name: 'description', 'Give it a short description:' }
])
// or
const { name, description } = await go.ask([
  { name: 'name', 'How to name your project?' },
  { name: 'description', 'Give it a short description:' }
])
```

### Question Types

#### Available Types

> [`when`](#when), [`prefix`](#prefix) and [`suffix`](#suffix) are available and optional for all types.

##### Input

`{ type: 'input' , `[`message`](#message)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`filter`](#filter)` , `[`validate`](#validate)` , `[`transformer`](#transformer)` ] }`

Basic text input.

##### Password

`{ type: 'password' , `[`message`](#message)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`filter`](#filter)` , `[`validate`](#validate)` , `[`mask`](#mask)` ] }`

It is like [Input](#input) but hides what was entered or replace it with [mask](#mask) string.

##### Confirm

`{ type: 'confirm' , `[`message`](#message)` [ , `[`name`](#name)` , `[`default`](#default)` ] }`

Suggest to enter `'y'` or `'n'` and if entered string starts with `'y'` or `'Y'` results to `true`, otherwise results to `false`.

##### List

`{ type: 'list' , `[`message`](#message)` , `[`choices`](#choices)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`filter`](#filter)` , `[`pageSize`](#pagesize)` ] }`

> Note that **default** must be the choice **index** in the array or a choice value.

Offer a list of options where the one can be selected using arrow keys (Up and Down).

##### Raw List

`{ type: 'rawlist' , `[`message`](#message)` , `[`choices`](#choices)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`filter`](#filter)` , `[`pageSize`](#pagesize)` ] }`

> Note that **default** must be the choice **index** in the array or a choice value.

Offer a list of options where the one can be selected by entering an index number.

##### Checkbox

`{ type: 'checkbox' , `[`message`](#message)` , `[`choices`](#choices)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`filter`](#filter)` , `[`validate`](#validate)` , `[`pageSize`](#pagesize)` ] }`

> Note that **default** must be an array of values that suppose to be selected.

Offer a list of options and let to choose several of them by navigation with arrow keys (Up and Down) and using Space to select an option.
Pressing `a` on keyboard will select all of the options and `i` will inverse all selctions.

Choices can have **disabled** key.
If **disabled** is truthy the option will be unselectable.
If **disabled** is a `string`, then the string will be outputted next to the disabled choice.
The **disabled** property can also be a synchronous `function` receiving the current answers as argument and returning a `boolean` or a `string`.

##### Autocomplete

`{ type: 'autocomplete' , `[`message`](#message)` , `[`source`](#source)` [ , `[`name`](#name)` , `[`filter`](#filter)` , `[`suggestOnly`](#suggestonly)` , `[`validate`](#validate)` , `[`pageSize`](#pagesize)` ] }`

Offer a list of options where the one can be selected using arrow keys (Up and Down) and the list can be filtered by typing text in.
Read how to filter [`source`](#source) list and how autocomplete can [`only suggest`](#suggestonly) options.

##### Editor

`{ type: 'editor' , `[`message`](#message)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`filter`](#filter)` , `[`validate`](#validate)` ] }`

Launches an instance of the users preferred editor on a temporary file.
Once the user exits their editor, the contents of the temporary file are read in as the result.
The editor to use is determined by reading the `$VISUAL` or `$EDITOR` environment variables.
If neither of those are present, **notepad** (Windows) or **vim** (Linux or Mac) is used.

##### Expand

`{ type: 'expand' , `[`message`](#message)` , `[`choices`](#choices)` [ , `[`name`](#name)` , `[`default`](#default)` , `[`pageSize`](#pagesize)` ] }`

> Note that **default** must be the choice **index** in the array or a choice value.
> If **default** key not provided, then **help** will be used as default choice.

Offer a list of options and let to choose one using a key alias.
**choices** object will take an extra parameter called **key**.
This parameter must be a single lowercased character.
The `'h'` option is added by the prompt to show a list of available options and shouldn't be defined by the user.

#### Duck Typing

It is not required to provide a **type** property to specify the question type.
There are some rules that are used to determine the type of a question if it is not specified.

1. If **type** is specified, it won't change, otherwise…
2. If **choices** object is presented
	1. If **multiple** property is truthy, then **type** is `'checkbox'`
	2. Otherwise, **type** is `'list'`
3. If **source** is presented, **type** is `'autocomplete'`
4. Otherwise, **type** is `'input'`

#### More Types

This is not the exhaustive list of question types.
You can add more types using [Inquirer plugins](https://www.npmjs.com/package/inquirer#plugins) with [`go.registerQuestion`](#registerquestion):

```js
const go = require('go')
go.use(require('go-plugin-quiz'))

go.registerQuestion('datetime', require('inquirer-datepicker-prompt'))
```

## Examples

> The examples that are using [async/await](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await) feature won't be covered in async function to reduce amount of code in examples.

### Ask for the basic text input

```js
go.ask('project name:')
  .then(name => console.log(`creating new project called ${name}…`))
```

### Ask a question with options

```js
go.ask('project name:', { default: 'my-project' })
```

### Question as an object

```js
go.ask({ message: 'project name:', default: 'my-project' })
```

### Ask a sequence of questions

```js
const [ name, dest ] = await go.ask([
  { message: 'project name', default: 'my-project' },
  'destination folder'
])
```

### Default options for multiple questions

```js
const [ name, dest ] = await go.ask([
  'project name:',
  'destination folder:'
], { default: 'my-project' })
```

### Named answers

```js
const { name, dest } = await go.ask([
  { name: 'name',
    message: 'project name',
    default: 'my-project' },

  { name: 'dest',
    message: 'destination folder' }
])
```

### Conditional questions

Using [`when`](#when) property let you choose in runtime which questions have to be skipped.

```js
const { dest } = await go.ask([
  { name: 'install',
    type: 'confirm',
    message: 'do you want to install extension pack?' },
  { name: 'dest',
    message: 'where to install it?',
    when: (answers) => answers.install }
])
```

### Input validation

[`validate`](#validate) property can be used to prevent entering incorrect data.

```js
const password = await go.ask({
  type: 'password',
  message: 'set password:',
  validate: (input) => {
    if (input.trim().length < 8) {
      return 'password can\'t contain less then 8 characters'
    }

    return true
  }
})
```

### Answer transformation

```js
const keep = await go.ask({
  type: 'confirm',
  message: 'Do you want to delete it?',
  transformer: answer => !answer
})

// with multiple answers

const { states, getCode } => require('./states')
const codes = await go.ask({
  message: 'Select states',
  multiple: true,
  choices: states,
  transform: selected => selected.map(state => getCode(state))
})
```

## License

MIT © [Stanislav Termosa](https://github.com/termosa)


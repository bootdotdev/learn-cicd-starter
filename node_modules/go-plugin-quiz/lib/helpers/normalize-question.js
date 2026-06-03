const { autocompleteFilter } = require('./autocomplete-filter')

const isFunction = object => typeof object === 'function'

const ensureType = (question) => {
  if (question.type) return question
  if (question.choices) return Object.assign({}, question, { type: question.multiple ? 'checkbox' : 'list' })
  if (question.source) return Object.assign({}, question, { type: 'autocomplete' })
  return Object.assign({}, question, { type: 'input' })
}

const wrapOption = (option, answers, argsLen = 0) => {
  if (!isFunction(option)) return option

  return function (...args) {
    return option.apply(this, [ ...args.slice(0, argsLen), answers ])
  }
}

const wrapChoices = (choices, answers) => {
  const wrapDisabled = (list) => {
    return list.map((choice) => {
      if (!choice || !isFunction(choice.disabled)) return choice
      return Object.assign({}, choice, { disabled: wrapOption(choice.disabled, answers) })
    })
  }

  if (Array.isArray(choices)) {
    return wrapDisabled(choices)
  }

  if (isFunction(choices)) {
    choices = wrapOption(choices, answers)
    return function (...args) {
      const options = choices.apply(this, args)
      if (Array.isArray(options)) {
        return wrapDisabled(options)
      }
      return options
    }
  }

  return choices
}

const wrapSource = (source, answers) => {
  if (isFunction(source)) {
    return function (_, input) {
      return Promise.resolve(source.call(this, input, answers))
    }
  }

  if (Array.isArray(source)) {
    return (_, input) => Promise.resolve(input ? source.filter(autocompleteFilter(input)) : source)
  }

  return source
}

const normalizeOptions = (question, answers) => {
  question.message = wrapOption(question.message, answers)
  question.default = wrapOption(question.default, answers)
  question.validate = wrapOption(question.validate, answers, 1)
  question.filter = wrapOption(question.filter, answers, 1)
  question.transformer = wrapOption(question.transformer, answers, 1)
  question.when = wrapOption(question.when, answers)

  question.choices = wrapChoices(question.choices, answers)
  question.source = wrapSource(question.source, answers)

  return question
}

const normalizeQuestion = (question, defaults, answers) => {
  question = typeof question === 'string'
    ? Object.assign({ type: 'input' }, defaults, { message: question })
    : Object.assign({}, defaults, question)

  question = ensureType(question)
  question = normalizeOptions(question, answers)

  return question
}

exports.normalizeQuestion = normalizeQuestion

const isEmpty = require('is-empty')
const { failGiven } = require('./fail-given')
const { normalizeCommandOptions } = require('./normalize-command-options')

const isDefined = value => typeof value !== 'undefined'

const validateCommand = (command) => {
  if (!command || typeof command !== 'object') {
    throw failGiven(command, '`command` should be an object')
  }

  if (typeof command.name !== 'string' || isEmpty(command.name.trim())) {
    throw failGiven(command.name, '`name` should be not empty string')
  }

  if (isDefined(command.callback) && typeof command.callback !== 'function') {
    throw failGiven(command.callback, '`callback` must be a function')
  }

  if (command.commands && (!Array.isArray(command.commands) || isEmpty(command.commands))) {
    throw failGiven(command.commands, '`commands` must be an array and it can not be empty')
  }

  if (command.description && typeof command.description !== 'string') {
    throw failGiven(command.description, '`description` must be a string')
  }

  if (command.title && typeof command.title !== 'string') {
    throw failGiven(command.title, '`title` must be a string')
  }

  if (command.prefix && typeof command.prefix !== 'string') {
    throw failGiven(command.prefix, '`prefix` must be a string')
  }

  if (!command.callback && !command.commands) {
    throw failGiven(command, '`command` should contain either `callback` function or `commands` array')
  }
}

const normalize = (command, inheritedOptions, parent) => {
  validateCommand(command) // will throw if fail

  const normalized = { name: command.name.trim() }

  if (command.callback) normalized.callback = command.callback
  if (command.description) normalized.description = command.description
  if (command.prefix) normalized.prefix = command.prefix
  if (command.title) normalized.title = command.title
  if (command.when) normalized.when = command.when

  if (parent) normalized.parent = parent
  if (command.options) normalized.options = normalizeCommandOptions(command.options, inheritedOptions)
  if (command.commands) normalized.commands = command.commands.map(c => normalize(c, normalized.options, normalized))

  return normalized
}

const normalizeCommand = (command) => normalize(command)

exports.normalizeCommand = normalizeCommand

const minimist = require('minimist')

const optionsToMinimist = (options = {}) => ({
  '--': true,
  boolean: Object.keys(options)
    .reduce((booleans, opt) => options[opt].type === Boolean ? booleans.concat(opt) : booleans, []),
  string: Object.keys(options)
    .reduce((strings, opt) => options[opt].type === String ? strings.concat(opt) : strings, []),
  default: Object.keys(options)
    .reduce((defaults, opt) => Object.assign(defaults, { [opt]: options[opt].default }), {}),
  alias: Object.keys(options)
    .reduce((aliases, opt) => Object.assign(aliases, { [opt]: options[opt].alias }), {})
})

const parseCommand = (commandRequest, options) =>
  minimist(commandRequest.trim().split(/\s+/g), optionsToMinimist(options))

exports.parseCommand = parseCommand

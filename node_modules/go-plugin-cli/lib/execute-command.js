const { parseCommand } = require('./parse-command')
const { matchCommand } = require('./match-command')

const executeCommand = (stash, commandString) => {
  if (!commandString || typeof commandString !== 'string') {
    throw new Error('`command` should be not empty string')
  }

  const command = matchCommand(stash, commandString)

  if (!command) {
    return Promise.reject(new Error('command is not registered'))
  }

  if (typeof command.callback !== 'function') {
    return Promise.reject(new Error('command doesn\'t have a callback'))
  }

  const args = parseCommand(commandString, command.options)
  return Promise.resolve(command.callback({ args }))
}

exports.executeCommand = executeCommand

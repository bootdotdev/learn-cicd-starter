const { prompt } = require('inquirer')
const chalk = require('chalk')

const guide = (commandTree, title = 'Choose command:', prefix = 'GO') => {
  if (!commandTree || !commandTree.length) {
    return Promise.reject(new Error('no commands found'))
  }

  const question = {
    name: 'command',
    message: title,
    type: 'list',
    prefix: chalk.blueBright(`[${prefix}]`),
    choices: commandTree
      .map((command) => ({
        name: command.name + (command.description ? chalk.gray(` — ${command.description}`) : ''),
        short: command.name,
        value: command,
        disabled: !!command.disabled
      }))
      .sort((commandA, commandB) => commandA.name > commandB.name ? 1 : -1)
  }

  return prompt([ question ])
    .then(({ command }) => {
      if (!Array.isArray(command.commands)) return command
      return guide(command.commands, command.title, command.prefix || command.name.toUpperCase())
    })
}

module.exports = guide

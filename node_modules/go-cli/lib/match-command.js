const guide = require('./guide')

const parseCommandNames = command => command.parent
  ? parseCommandNames(command.parent).concat(command.name)
  : [command.name]

const matchCommand = (args, env) => new Promise((resolve) => {
  if (!env.configPath || !env.modulePath) return resolve(null)

  const go = require(env.modulePath)
  // initialize local Gofile
  require(env.configPath)

  if (!args.length) {
    return resolve(() => guide(go.getCommands()).then(command => {
      const args = { _: parseCommandNames(command) }
      command.callback({ args })
    }))
  }

  if (!go.getCommands().length) return resolve(null)

  const commandString = args.join(' ')
  const command = go.matchCommand(commandString)
  if (!command) return resolve(null)

  resolve(() => go.executeCommand(commandString))
})

module.exports = matchCommand

const Liftoff = require('liftoff')
const interpret = require('interpret')
const parse = require('minimist')
const invoke = require('./invoke')

const go = (args) => new Promise((resolve, reject) => {
  const argv = parse(args)

  const Cli = new Liftoff({
    name: 'go',
    processTitle: ['go'].concat(args).join(' '),
    extensions: interpret.jsVariants
  })

  const run = (env) =>
    invoke(args, env).then(resolve, reject)

  Cli.launch({
    cwd: argv.cwd,
    configPath: argv.config,
    require: argv.require,
    completion: argv.completion
  }, run)
})

module.exports = go

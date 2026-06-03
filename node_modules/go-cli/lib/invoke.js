const matchCommand = require('./match-command')
const matchLoader = require('./match-loader')
const matchBinary = require('./match-binary')

const matchers = [
  matchCommand,
  matchLoader,
  matchBinary
]

const findExecutor = (matchers, args, env) => {
  if (!matchers.length) return Promise.resolve(null)
  return matchers[0](args, env)
    .then((executor) => {
      if (executor) return executor
      return findExecutor(matchers.slice(1), args, env)
    })
}

const invoke = (args, env) =>
  findExecutor(matchers, args, env)
    .then((executor) => {
      if (executor) return executor()
      throw new Error('command is not recognized')
    })

module.exports = invoke

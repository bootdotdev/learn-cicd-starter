const minimist = require('minimist')

const parseArgs = (args = []) => minimist(args, {
  boolean: [
    'install',
    'keep-git'
  ],
  strings: [
    'checkout',
    'depth',
    'git'
  ],
  alias: {
    'keep-git': ['k']
  },
  default: {
    'install': true,
    'keep-git': false
  }
})

module.exports = parseArgs

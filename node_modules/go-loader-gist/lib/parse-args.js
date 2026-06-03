const minimist = require('minimist')

const parseArgs = (args = []) => minimist(args, {
  boolean: [
    'install'
  ],
  default: {
    'install': true
  }
})

module.exports = parseArgs

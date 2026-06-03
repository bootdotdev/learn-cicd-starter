const { display } = require('./display')

const failGiven = (value, message) => {
  throw new Error(`${message} (given: ${JSON.stringify(display(value))})`)
}

exports.failGiven = failGiven

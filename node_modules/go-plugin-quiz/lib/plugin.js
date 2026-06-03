const { ask } = require('./ask')
const { confirm } = require('./confirm')
const { registerQuestion } = require('./register-question')
const inquirer = require('inquirer')
const autocompletePrompt = require('inquirer-autocomplete-prompt')

inquirer.registerPrompt('autocomplete', autocompletePrompt)

const QuizPlugin = (proto = {}) => {
  proto.inquirer = inquirer
  proto.ask = ask
  proto.confirm = confirm
  proto.registerQuestion = registerQuestion

  return proto
}

exports.QuizPlugin = QuizPlugin
exports.install = QuizPlugin

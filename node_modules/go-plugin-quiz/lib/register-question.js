const inquirer = require('inquirer')

const registerQuestion = (type, question) => {
  try {
    inquirer.registerPrompt(type, question)
  } catch (error) {
    throw error
  }
}

exports.registerQuestion = registerQuestion

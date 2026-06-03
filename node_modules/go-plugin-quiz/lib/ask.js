const inquirer = require('inquirer')
const { prompt } = require('./helpers/prompt')

const ask = (questions, options = {}) => {
  if (!questions) {
    throw new Error(`ask(${JSON.stringify(questions)}) has nothing to ask`)
  }

  const multipleAnswers = Array.isArray(questions)
  if (!Array.isArray(questions)) questions = [questions]

  return prompt(questions, options)
    .then((answers) => multipleAnswers ? answers : answers[0])
    .catch((error) => { throw error })
}

ask.separator = (...args) => new inquirer.Separator(...args)

exports.ask = ask

const inquirer = require('inquirer')
const { normalizeQuestion } = require('./normalize-question')
const { chainQuestions } = require('./chain-questions')
const { uid } = require('./uid')

const prompt = (questions, defaults = {}) => {
  const prompt = inquirer.prompt

  const answers = []
  answers._ = {}

  questions = questions
    .map(question => normalizeQuestion(question, defaults, answers))
    .map(question => Object.assign({}, question, { _alias: question.name, name: uid() }))
    .map(question => () => {
      return prompt(question)
        .then(answers => answers[question.name])
        .then(answer => {
          answers.push(answer)
          if (question._alias) {
            answers[question._alias] = answer
            answers._[question._alias] = answer
          }
        })
    })

  return chainQuestions(questions).then(() => answers)
}

exports.prompt = prompt

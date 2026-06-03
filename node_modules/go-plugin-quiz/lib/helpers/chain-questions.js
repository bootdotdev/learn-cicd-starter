const chainQuestions = (questions) => {
  if (!questions.length) return Promise.resolve()
  return questions[0]().then(() => chainQuestions(questions.slice(1)))
}

exports.chainQuestions = chainQuestions

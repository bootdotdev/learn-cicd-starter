var go = require('./go')()

var CLIPlugin = require('go-plugin-cli')
var FSPlugin = require('go-plugin-fs')
var QuizPlugin = require('go-plugin-quiz')
var TemplatesPlugin = require('go-plugin-templates')

module.exports = go
  .use(CLIPlugin)
  .use(FSPlugin)
  .use(QuizPlugin)
  .use(TemplatesPlugin)

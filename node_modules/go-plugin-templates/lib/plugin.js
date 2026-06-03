const { createTemplate } = require('./create-template')
const { loadTemplates } = require('./load-templates')
const { processTemplates } = require('./process-templates')

const TemplatesPlugin = (proto = {}) => {
  proto.createTemplate = createTemplate
  proto.loadTemplates = loadTemplates
  proto.processTemplates = processTemplates

  return proto
}

exports.TemplatesPlugin = TemplatesPlugin
exports.install = TemplatesPlugin

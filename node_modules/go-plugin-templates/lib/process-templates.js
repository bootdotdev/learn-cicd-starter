const { loadTemplates } = require('./load-templates')

const processTemplates = (context, search, options) =>
  loadTemplates(search, options)
    .then((templates) => templates.write(context))

processTemplates.sync = (context, search, options) =>
  loadTemplates.sync(search, options).write.sync(context)

exports.processTemplates = processTemplates

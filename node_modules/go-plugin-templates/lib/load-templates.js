const fs = require('fs-extra')
const { resolve } = require('path')
const { createTemplate } = require('./create-template')
const globby = require('globby')
const { normalizeSearch } = require('./normalize-search')

const wrapTemplates = (templates) => {
  templates.write = (context, resolvePath) =>
    Promise.all(templates.map((t) => t.write(context, resolvePath))).then(() => {})

  templates.write.sync = (context, resolvePath) => {
    templates.map((t) => t.write.sync(context, resolvePath))
  }

  return templates
}

const loadFiles = (files, cwd) => {
  const loadingFiles = files.map((name) => {
    return fs.readFile(resolve(cwd, name))
      .then(content => ({ content, name }))
  })

  return Promise.all(loadingFiles)
}

const createTemplatesFromFiles = (files, options) =>
  files.map(({ content, name }) => {
    const extra = { filename: name }
    return createTemplate(
      content.toString(),
      options
        ? Object.assign({}, typeof options === 'object' ? options : { resolve: options }, extra)
        : extra
    )
  })

const loadTemplates = (search, options) => {
  search = normalizeSearch(search)
  return globby(search.patterns, search)
    .then((files) => loadFiles(files, search.cwd))
    .then((files) => createTemplatesFromFiles(files, options))
    .then(wrapTemplates)
}

loadTemplates.sync = (search, options) => {
  search = normalizeSearch(search)
  const files = globby.sync(search.patterns, search)
    .map((name) => ({ name, content: fs.readFileSync(resolve(search.cwd, name)) }))
  const templates = createTemplatesFromFiles(files, options)

  return wrapTemplates(templates)
}

exports.loadTemplates = loadTemplates

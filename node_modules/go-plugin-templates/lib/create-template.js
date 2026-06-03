const ejs = require('ejs')
const fs = require('fs-extra')
const { sep } = require('path')
const { resolveDestination } = require('./resolve-destination')

const normalizeOptions = (options = {}) => Object.assign(
  {},
  options,
  { escape: typeof options.escape === 'function' ? options.escape : (str) => str }
)

const createTemplate = (template, options) => {
  if (typeof template !== 'string') {
    throw new Error('template argument should be a string')
  }

  options = normalizeOptions(options)

  // TODO: catch error and show it above the method
  const ejsTemplate = ejs.compile(template, options)

  const { filename } = options
  const getSource = () => filename

  const render = (context = {}) => ejsTemplate(context)

  const write = (context, resolvePath) => {
    const dest = resolveDestination(resolvePath || options.resolve, filename)

    if (!dest) {
      throw new Error('resolvePath and/or filename should be specified')
    }

    return fs.outputFile(dest, render(context))
      .then(() => Promise.resolve())
      .catch((error) => {
        if (/EISDIR/.test(error)) {
          throw new Error(
            `'${dest}' is a folder and it can not be rewritten\n` +
            `Tip: if you mean to write template into this directory add ${sep} at the end of the destination path`
          )
        } else {
          throw error
        }
      })
  }

  write.sync = (context, resolvePath) => {
    const dest = resolveDestination(resolvePath || options.resolve, filename)

    if (!dest) {
      throw new Error('resolvePath and/or filename should be specified')
    }

    try {
      fs.outputFileSync(dest, render(context))
    } catch (error) {
      if (/EISDIR/.test(error)) {
        throw new Error(
          `'${dest}' is a folder and it can not be rewritten\n` +
          `Tip: if you mean to write template into this directory add ${sep} at the end of the destination path`
        )
      } else {
        throw error
      }
    }
  }

  return { getSource, render, write }
}

exports.createTemplate = createTemplate

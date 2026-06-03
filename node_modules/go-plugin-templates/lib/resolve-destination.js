const ejs = require('ejs')
const { parse, sep } = require('path')

const resolveDestination = (resolver, filename) => {
  if (!resolver) {
    return filename
  }

  const meta = filename ? Object.assign(parse(filename), { filename }) : {}

  if (typeof resolver === 'function') {
    return resolver(meta)
  }

  if (typeof resolver !== 'string') {
    throw new Error('resolver argument should be a string or a function')
  }

  if (resolver.endsWith(sep)) {
    if (!filename) {
      throw new Error('filename argument should be specified when resolvePath is a folder')
    }

    resolver = ejs.compile(resolver + filename)
  } else {
    resolver = ejs.compile(resolver)
  }

  return resolver(meta)
}

exports.resolveDestination = resolveDestination

const resolveGlobal = require('resolve-global')

const LOADER_PREFIX = 'go-loader-'

const normalizeLoaderName = (name) => typeof name === 'string'
  ? LOADER_PREFIX + name.trim().toLowerCase()
  : null

const resolveLoader = (name) => {
  try {
    return require.resolve(name)
  } catch (err) {
    return resolveGlobal.silent(name)
  }
}

const requireLoader = (name) => {
  const loaderPath = resolveLoader(name)
  if (!loaderPath) return null
  return require(loaderPath)
}

module.exports.requireLoader = requireLoader
module.exports.normalizeLoaderName = normalizeLoaderName

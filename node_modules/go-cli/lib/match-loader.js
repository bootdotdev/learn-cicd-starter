const { requireLoader, normalizeLoaderName } = require('./utils')
const installPackage = require('./install-package')

const GIT_LOADER_NAME = 'git'
const GITHUB_LOADER_NAME = 'github'

const matchLoader = (args, env) => new Promise((resolve, reject) => {
  const firstValue = args[0]
  const isGitLoader = /^(git@|https:\/\/).+\.git$/i.test(firstValue)
  const isGithubLoader = !isGitLoader && /^[a-z].+\/[-_a-z\d]+(:[^\s]+)?$/i.test(firstValue)
  const loaderName = normalizeLoaderName(
    (isGitLoader && GIT_LOADER_NAME) || (isGithubLoader && GITHUB_LOADER_NAME) || firstValue
  )
  if (!loaderName) return resolve(null)

  const loader = requireLoader(loaderName)
  if (!loader) return resolve(null)

  if (!loader || typeof loader.execute !== 'function') {
    return reject(new Error(`${loaderName} should export 'execute' method`))
  }

  const processResult = (result) => {
    if (result && result.install && result.path) {
      return installPackage(result.path)
    }
  }

  const executor = () => new Promise((resolve) => {
    const newArgs = (isGitLoader && [GIT_LOADER_NAME, ...args]) ||
      (isGithubLoader && [GITHUB_LOADER_NAME, ...args]) || args
    resolve(loader.execute({ args: newArgs, env }))
  }).then(processResult)

  resolve(executor)
})

module.exports = matchLoader

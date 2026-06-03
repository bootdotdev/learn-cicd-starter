const parseArgs = require('go-loader-git/lib/parse-args')
const isValidTarget = require('go-loader-git/lib/is-valid-target')
const setup = require('go-loader-git/lib/setup')
const isValidSource = require('./is-valid-source')

const loadGithub = ({ args }) => {
  const argv = parseArgs(args)
  const firstArgument = argv._[1]

  if (!isValidSource(firstArgument)) {
    const error = new Error('source should be a Github repository name specified as username/repository')
    return Promise.reject(error)
  }

  const [source, reference] = firstArgument.split(':')
  const repository = `git@github.com:${source}.git`
  const destination = argv._[2] || source.split('/')[1]

  if (reference) argv.checkout = reference

  return isValidTarget(destination)
    .then(() => setup(repository, destination, argv))
    .then(() => ({ path: destination, install: argv.install }))
    .catch((error) => {
      throw new Error(`failed to load source because of '${error.message}'`)
    })
}

module.exports.execute = loadGithub

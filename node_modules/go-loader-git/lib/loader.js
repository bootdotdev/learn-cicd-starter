const extractDestination = require('./extract-destination')
const isGiturl = require('is-git-url')
const isValidTarget = require('./is-valid-target')
const parseArgs = require('./parse-args')
const setup = require('./setup')

const loadGit = ({ args }) => {
  const argv = parseArgs(args)
  const repo = argv._[1]

  if (!repo) {
    return Promise.reject(new Error(`failed to load repository: source is not specified`))
  }

  if (!isGiturl(repo)) {
    return Promise.reject(new Error(`failed to load repository: '${repo}' is not valid git link`))
  }

  const destination = argv._[2] || extractDestination(repo)

  return isValidTarget(destination)
    .then(() => setup(repo, destination, argv))
    .then(() => ({ path: destination, install: !!argv.install }))
    .catch((error) => {
      throw new Error(`failed to load repository because of '${error.message}'`)
    })
}

module.exports.execute = loadGit

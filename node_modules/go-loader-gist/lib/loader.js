const isValidSource = require('./is-valid-source')
const isValidTarget = require('./is-valid-target')
const loadGistFiles = require('./load-gist-files')
const parseArgs = require('./parse-args')
const saveFiles = require('./save-files')
const { sep } = require('path')

const loadGist = ({ args }) => {
  const cwd = process.cwd()
  const argv = parseArgs(args)
  const source = argv._[1]
  const destination = argv._[2] || cwd

  if (!source) {
    return Promise.reject(new Error('failed to load: gist is not specified'))
  }

  if (!isValidSource(source)) {
    return Promise.reject(new Error('failed to load: source suppose to be a valid gist hash'))
  }

  return isValidTarget(destination)
    .then(() => console.log('loading files...'))
    .then(() => loadGistFiles(source))
    .then(files => saveFiles(files, destination))
    .then(files => {
      const formattedFiles = files
        .map(name => name.startsWith(cwd) ? name.slice(cwd.length + sep.length) : name)
      console.log(`${files.length} file(s) were created:\n ${formattedFiles.join('\n ')}`)
    })
    .then(() => ({ path: destination, install: argv.install }))
    .catch((error) => {
      throw new Error(`failed to load: '${error.message ? error.message : error}'`)
    })
}

module.exports.execute = loadGist

const load = require('./load')

const parseJsonResponse = response => JSON.parse(response)

const parseFiles = response => {
  if (response.message) throw response.message
  return Object.keys(response.files)
    .map(name => response.files[name])
}

const loadFile = file =>
  load(file.raw_url)
    .then(content => Object.assign({}, file, { content, truncated: false }))

const loadTruncatedFiles = files =>
  Promise.all(files.map(file => file.truncated ? loadFile(file) : file))

const sourceToOptions = source => ({
  headers: { 'User-Agent': 'NodeJS' },
  hostname: 'api.github.com',
  path: `/gists/${source.toLowerCase()}`
})

const loadGistFiles = source => load(sourceToOptions(source))
  .then(parseJsonResponse)
  .then(parseFiles)
  .then(loadTruncatedFiles)

module.exports = loadGistFiles

const { resolve } = require('path')

const defaultIgnore = [
  '.git/**',
  '**/.git/**',
  './**/.git/**',
  'node_modules/**',
  '**/node_modules/**',
  './**/node_modules/**'
]

const defaultPattern = '**'

const isDefined = (value) => typeof value !== 'undefined'

const normalizeSearch = (search) => {
  if (typeof search === 'string') {
    search = { pattern: search }
  }

  if (search instanceof Array) {
    search = { patterns: search }
  }

  if (!search) {
    search = { pattern: defaultPattern }
  }

  if (typeof search !== 'object') {
    throw new Error('seach argument should be a string, an array or an object')
  }

  const opts = {}

  if (isDefined(search.brace)) { opts.brace = search.brace }
  if (isDefined(search.case)) { opts.case = search.case }
  if (isDefined(search.deep)) { opts.deep = search.deep }
  if (isDefined(search.expandDirectories)) { opts.expandDirectories = search.expandDirectories }
  if (isDefined(search.extension)) { opts.extension = search.extension }
  if (isDefined(search.followSymlinkedDirectories)) {
    opts.followSymlinkedDirectories = search.followSymlinkedDirectories
  }
  if (isDefined(search.gitignore)) { opts.gitignore = search.gitignore }
  if (isDefined(search.globstar)) { opts.globstar = search.globstar }
  if (isDefined(search.matchBase)) { opts.matchBase = search.matchBase }
  if (isDefined(search.nobrace)) { opts.nobrace = search.nobrace }
  if (isDefined(search.nocase)) { opts.nocase = search.nocase }
  if (isDefined(search.noext)) { opts.noext = search.noext }
  if (isDefined(search.noglobstar)) { opts.noglobstar = search.noglobstar }
  if (isDefined(search.transform)) { opts.transform = search.transform }
  if (isDefined(search.unique)) { opts.unique = search.unique }

  opts.cwd = typeof search.cwd === 'undefined' ? process.cwd() : resolve(process.cwd(), search.cwd)
  opts.dot = typeof search.dot === 'undefined' ? true : search.dot
  opts.ignore = typeof search.ignore === 'undefined' ? defaultIgnore : search.ignore

  opts.patterns = (search.patterns || []).concat(search.pattern ? search.pattern : [])
  if (!opts.patterns.length) {
    opts.patterns.push(defaultPattern)
  }

  return opts
}

exports.normalizeSearch = normalizeSearch

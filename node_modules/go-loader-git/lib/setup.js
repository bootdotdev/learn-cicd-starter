const clone = require('./clone')
const log = require('./log')
const rimraf = require('rimraf')
const { sep } = require('path')

const removeGit = (destination) => new Promise((resolve, reject) => {
  rimraf(destination + sep + '.git', (error) => {
    if (error) reject(error)
    else resolve()
  })
})

const setup = (repo, destination, argv) => {
  log(`(git) loading ${repo}`)
  return clone(repo, destination, argv)
    .then(() => {
      log(`(git) repository loaded to ${destination}`)
      if (argv['keep-git'] || typeof argv.depth !== 'undefined') return
      return removeGit(destination)
    })
}

module.exports = setup

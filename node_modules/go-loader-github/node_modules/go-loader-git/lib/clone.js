const { spawn } = require('child_process')

const GIT_BINARY = 'git'

const checkout = (git, target, link) => new Promise((resolve, reject) => {
  const args = ['checkout', link]
  spawn(git, args, { cwd: target })
    .on('close', (statusCode) => {
      if (!statusCode) resolve()
      else reject(new Error(`'${git} ${args.join(' ')}' failed with status ${statusCode}`))
    })
})

const clone = (repo, target = null, opts = {}) =>
  new Promise((resolve, reject) => {
    const git = opts.git || GIT_BINARY
    const args = ['clone']

    if (opts.depth) {
      args.push('--depth')
      args.push(opts.depth)
    } else if (!opts['keep-git'] && !opts.checkout && opts.depth !== false) {
      args.push('--depth')
      args.push(1)
    }

    args.push('--')
    args.push(repo)

    if (target) {
      args.push(target)
    }

    spawn(git, args)
      .on('close', (statusCode) => {
        if (statusCode) {
          reject(new Error(`'${git} ${args.join(' ')}' failed with status ${statusCode}`))
        } else if (opts.checkout) {
          resolve(checkout(git, target, opts.checkout))
        } else {
          resolve()
        }
      })
  })

module.exports = clone

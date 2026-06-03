const { statSync } = require('fs')
const { resolve: resolvePath } = require('path')
const { spawn } = require('child_process')

const CONFIG_FILE = '.goconfig'

const installPackage = (path) => new Promise((resolve, reject) => {
  const configPath = resolvePath('.', path, CONFIG_FILE)

  try {
    statSync(configPath)
  } catch (oO) {
    try {
      statSync(configPath + '.json')
    } catch (oO) {
      return resolve(`skip installation: ${CONFIG_FILE}(.json) file is not found`)
    }
  }

  const config = require(configPath)
  if (!config || !config.install) return resolve()

  spawn(config.install, { stdio: 'inherit', shell: true, cwd: path })
    .on('error', reject)
    .on('exit', (code) => {
      if (code) {
        const error = new Error('install command has failed')
        error.code = code
        return reject(error)
      }

      resolve()
    })
})

module.exports = installPackage

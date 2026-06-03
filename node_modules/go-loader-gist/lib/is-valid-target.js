const { readdir, stat } = require('fs')

const isValidTarget = (path) => new Promise((resolve, reject) => {
  stat(path, (error, stats) => {
    if (error) return resolve()

    const checkDir = error => {
      if (!error) resolve()
      else reject(new Error(`can not access '${path}' because of '${error}'`))
    }

    if (stats.isDirectory()) {
      readdir(path, checkDir)
    } else {
      reject(new Error(`'${path}' is a file`))
    }
  })
})

module.exports = isValidTarget

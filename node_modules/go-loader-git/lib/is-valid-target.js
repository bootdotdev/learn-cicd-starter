const { readdir, stat } = require('fs')

const isValidTarget = (path) => new Promise((resolve, reject) => {
  stat(path, (error, stats) => {
    if (error) return resolve()

    const checkDir = (error, items) => {
      if (error) {
        return reject(new Error(`can not access '${path}' because of '${error}'`))
      }

      if (!items || !items.length) resolve()
      else reject(new Error(`'${path}' is not empty`))
    }

    if (stats.isDirectory()) {
      readdir(path, checkDir)
    } else {
      reject(new Error(`'${path}' is a file`))
    }
  })
})

module.exports = isValidTarget

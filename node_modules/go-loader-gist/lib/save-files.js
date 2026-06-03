const ensureDir = require('mkdirp')
const fs = require('fs')
const { join } = require('path')

const encoding = 'utf8'

const writeFile = (path, content) => new Promise((resolve, reject) => {
  fs.writeFile(path, content, encoding, err => {
    if (err) reject(err)
    else resolve(path)
  })
})

const saveFiles = (files, destination) => new Promise((resolve, reject) => {
  if (!files.length) {
    return reject(new Error('Gist doesn\'t contain files'))
  }

  ensureDir.sync(destination)
  const saving = files
    .map(({ filename, content }) => writeFile(join(destination, filename), content))

  Promise.all(saving).then(resolve, reject)
})

module.exports = saveFiles

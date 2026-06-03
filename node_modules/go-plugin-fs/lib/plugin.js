const fs = require('fs-extra')

const FsPlugin = (proto) => {
  proto.fs = fs

  proto.copy = fs.copy.bind(fs)
  proto.copySync = fs.copySync.bind(fs)

  proto.move = fs.move.bind(fs)
  proto.moveSync = fs.moveSync.bind(fs)

  proto.remove = fs.remove.bind(fs)
  proto.removeSync = fs.removeSync.bind(fs)

  proto.writeFile = fs.outputFile.bind(fs)
  proto.writeFileSync = fs.outputFileSync.bind(fs)

  proto.readFile = fs.readFile.bind(fs)
  proto.readFileSync = fs.readFileSync.bind(fs)

  proto.createDir = fs.ensureDir.bind(fs)
  proto.createDirSync = fs.ensureDirSync.bind(fs)

  return proto
}

exports.FsPlugin = FsPlugin
exports.install = FsPlugin

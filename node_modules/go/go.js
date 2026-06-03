function use (plugin, options = {}) {
  if (this instanceof Go) {
    if (matchPlugin(plugin, this)) return this

    if (plugin && typeof plugin.install === 'function') {
      plugin.install(this, options)
      this._plugins.push(plugin.install)
    } else if (typeof plugin === 'function') {
      plugin(this, options)
      this._plugins.push(plugin)
    } else {
      throw new ReferenceError('\'plugin\' must be a function or an object with install method')
    }

    return this
  } else {
    throw new ReferenceError('use() should be called on instance of Go')
  }
}

function isUsed (plugin) {
  if (this instanceof Go) {
    if (plugin && typeof plugin.install === 'function') {
      plugin = plugin.install
    }
    return matchPlugin(plugin, this)
  } else {
    throw new ReferenceError('isUsed() should be called on instance of Go')
  }
}

function matchPlugin (plugin, instance) {
  for (let i = instance._plugins.length; i--;) {
    if (instance._plugins[i] === plugin) return true
  }
  return false
}

let shouldCreateRealInstance = false

function Go () {
  if (!shouldCreateRealInstance) {
    shouldCreateRealInstance = true
    const go = new Go()
    shouldCreateRealInstance = false
    return go
  }
  this._plugins = []
}

Go.prototype.use = use
Go.prototype.isUsed = isUsed

module.exports = Go

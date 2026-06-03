const isValidSource = source => /^[\da-f]+(\/[\da-f]+)?$/i.test(source)

module.exports = isValidSource

const display = (value) => {
  if (!value) {
    return value
  }

  if (typeof value === 'function') {
    return value.toString()
  }

  if (typeof value !== 'object') {
    return value
  }

  if (Array.isArray(value)) {
    return value.map(display)
  }

  return Object.keys(value)
    .reduce((result, key) => Object.assign({ [key]: display(value[key]) }, result), {})
}

exports.display = display

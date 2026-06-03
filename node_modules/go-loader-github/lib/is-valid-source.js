const isValidSource = (source) => {
  return /^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}\/[-_a-z\d]{1,100}(:[^\s]+)?$/i.test(source)
}

module.exports = isValidSource

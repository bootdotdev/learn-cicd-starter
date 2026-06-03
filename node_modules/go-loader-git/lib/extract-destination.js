const extractDestination = (repository) => {
  const name = repository.match(/(^|:|\/)([^/:]+)\/*(.git)?\/*$/i)[2]
  if (!name.endsWith('.git')) return name
  return name.slice(0, -4)
}

module.exports = extractDestination

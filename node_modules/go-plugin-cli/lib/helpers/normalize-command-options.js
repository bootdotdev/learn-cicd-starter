const uniq = require('uniq')
const { failGiven } = require('./fail-given')
const { display } = require('./display')

const isDefined = value => typeof value !== 'undefined'

const OPTION_TYPES = [String, Boolean]

const validateAliasInterpolation = (options) => {
  const optionsNames = Object.keys(options)

  const allAliases = optionsNames
    .map(option => options[option].alias)
    .reduce((allAliases, aliases) => allAliases.concat(aliases), [])
    .sort()

  const uniqAliases = uniq(allAliases.slice(0)).sort()
  if (allAliases.length === uniqAliases.length) return

  const alias = allAliases.find((alias, index) => alias !== uniqAliases[index])
  optionsNames.filter(option => options[option].alias.includes(alias))
  throw new Error(`aliases can not be redefined in inherited options (\`v\` is used for \`${optionsNames.join('`, `')}\`)`)
}

const normalizeCommandOption = (name, option, inheritedOption = {}) => {
  if (!option || (!OPTION_TYPES.includes(option) && typeof option !== 'object')) {
    throw failGiven(option, '`option` should be either Boolean, String or Object({ type, default, alias })')
  }

  if (OPTION_TYPES.includes(option)) {
    option = { type: option }
  }

  if (option.type && !OPTION_TYPES.includes(option.type)) {
    throw failGiven(option.type, `\`${name}.type\` should be either Boolean or String`)
  }

  if (option.alias && typeof option.alias !== 'string') {
    if (!Array.isArray(option.alias)) {
      throw failGiven(option.alias, `\`${name}.alias\` should be a string or an array of strings`)
    }

    if (!option.alias.every(alias => typeof alias === 'string')) {
      throw failGiven(option.alias, `\`${name}.alias\` should be a string or an array of strings`)
    }
  }

  if (option.type && inheritedOption.type && option.type !== inheritedOption.type) {
    const definedAs = inheritedOption.type === Boolean ? 'Boolean' : 'String'
    const errorMessage = `\`${name}.type\` is defined in parent command as \`${definedAs}\` and can not be redefined`
    throw new Error(errorMessage + ` (given: ${definedAs === 'Boolean' ? 'String' : 'Boolean'})`)
  }

  if (isDefined(option.default) && isDefined(inheritedOption.default) && option.default !== inheritedOption.default) {
    const definedAs = display(inheritedOption.default)
    const errorMessage = `\`${name}.default\` is defined in parent command as \`${definedAs}\` and can not be redefined`
    throw failGiven(option.default, errorMessage)
  }

  const alias = option.alias ? typeof option.alias === 'string' ? [option.alias] : option.alias : []

  return {
    type: option.type || inheritedOption.type || String,
    default: isDefined(option.default) ? option.default : inheritedOption.default,
    alias: uniq(alias.concat(inheritedOption.alias || []))
  }
}

const normalizeCommandOptions = (options, inheritedOptions = {}) => {
  const normalized = Object.keys(options)
    .reduce((newOptions, key) => Object.assign(newOptions, {
      [key]: normalizeCommandOption(key, options[key], inheritedOptions[key])
    }), Object.assign({}, inheritedOptions))

  validateAliasInterpolation(normalized)

  return normalized
}

exports.normalizeCommandOptions = normalizeCommandOptions

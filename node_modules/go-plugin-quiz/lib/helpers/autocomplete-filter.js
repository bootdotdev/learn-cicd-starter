const autocompleteFilter = (input) =>
  (option) => new RegExp(input, 'i').exec(option) !== null

exports.autocompleteFilter = autocompleteFilter

const https = require('https')

const load = (urlOptions) => new Promise((resolve, reject) => {
  https.get(urlOptions, stream => {
    let response = ''
    stream.on('data', chunk => { response += chunk })
    stream.on('end', () => resolve(response))
  }).on('error', reject).end()
})

module.exports = load

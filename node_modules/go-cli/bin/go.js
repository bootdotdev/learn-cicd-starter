#!/usr/bin/env node

const go = require('..')
const args = process.argv.slice(2)
go(args).catch(error => {
  if (!error) process.exit(1)

  if (error.message || !(error instanceof Error)) {
    console.error(error)
  }
  process.exit(error.code || 1)
})

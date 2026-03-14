#!/usr/bin/env bash

set -e

t=$(mktemp -t cover.XXXXX)

go test $COVERFLAGS -coverprofile=$t "$@"

go tool cover -func=$t

unlink $t
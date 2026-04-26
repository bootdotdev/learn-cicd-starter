#!/bin/bash

set -a
source .env
set +a

go clean

go build .

./notely

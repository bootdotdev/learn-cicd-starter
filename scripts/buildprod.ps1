$Env:GOOS = "linux"; $Env:CGO_ENABLED = 0; $Env:GOARCH="amd64"; go build -o notely -buildvcs=false

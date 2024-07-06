run: build
	@bin/notely --debug

build:
	@go build -o bin/notely
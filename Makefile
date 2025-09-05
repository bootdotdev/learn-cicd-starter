build:
	@go build -o ./out/notely

run: build
	@./out/notely

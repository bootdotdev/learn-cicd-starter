# learn-cicd-starter (Notely)

This repo contains the starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).

## Local Development

Make sure you're on Go version 1.20+.

Create a `.env` file in the root of the project with the following contents:

```bash
PORT="8080"
```

Run the server:

```bash
go build -o notely && ./notely
```

*This starts the server in non-database mode.* It will serve a simple webpage at `http://localhost:8080`.

You do *not* need to set up a database or any interactivity on the webpage yet. Instructions for that will come later in the course!

//* Adding updates for tests again & running the ci by pr


RUNNING TESTS
Our current CI doesn't do anything interesting.

A good CI pipeline typically includes unit tests, integration tests, styling checks, linting checks, security checks or any other type of automated test. If any of the tests fail, the build is considered broken and the developer is notified so they can fix it.
//* writing unit tests*//
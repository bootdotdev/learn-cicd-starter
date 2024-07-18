# learn-cicd-starter (Notely)

![code coverage badge](https://github.com/barturba/learn-cicd-starter/actions/workflows/ci.yml/badge.svg)

This repo contains the starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).

## Local Development

Make sure you're on Go version 1.22+.

Create a `.env` file in the root of the project with the following contents:

```bash
PORT="8080"
```

Run the server:

```bash
go build -o notely && ./notely
```

_This starts the server in non-database mode._ It will serve a simple webpage at `http://localhost:8080`.

You do _not_ need to set up a database or any interactivity on the webpage yet. Instructions for that will come later in the course!

## Technologies

This project utilizes the following technologies:

- [chi router](https://github.com/go-chi/chi) for routing
- `database/sql` for database operations
- `embed` for embedding static files
- `io` for input/output operations
- `log` for logging
- `net/http` for HTTP server functionality
- `os` for operating system related operations
- [cors](https://github.com/go-chi/cors) for Cross-Origin Resource Sharing (CORS) support
- [godotenv](https://github.com/joho/godotenv) for loading environment variables from a `.env` file
- [libsql-client-go](https://github.com/tursodatabase/libsql-client-go/libsql) for database connectivity

Please make sure to have these dependencies installed and configured properly before running the application.

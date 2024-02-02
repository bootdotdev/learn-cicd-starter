# learn-cicd-starter (Notely)

This repo contains the starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).

## Local Development

Make sure you're on Go version 1.20+.

Create a `.env` file in the root of the project with the following contents:

```bash
PORT="8000"
```

Adding this comment in main for branch testing purposes

Run the server:

```bash
go build -o notely && ./notely
```

_This starts the server in non-database mode._ It will serve a simple webpage at `http://localhost:8000`.

You do _not_ need to set up a database or any interactivity on the webpage yet. Instructions for that will come later in the course!

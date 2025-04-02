# learn-cicd-starter (Notely)

![code coverage badge](https://github.com/HocusLocusTee/learn-cicd-starter/actions/workflows/.github/workflows/ci.yml/badge.svg)

This repo contains the starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).

## Local Development

go

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

  git config --global user.email "182385655+HocusLocusTee@users.noreply.github.com"
  git config --global user.name "Your Name"

MYNAME's version of Boot.dev's Notely app.

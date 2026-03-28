# learn-cicd-typescript-starter (Notely)

![Test Result](https://github.com/Gautham116006/learn-cicd-starter/actions/workflows/ci.yml/badge.svg)

This repo contains the typescript starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).

## Local Development

Make sure you're on Node version 22+.

Create a `.env` file in the root of the project with the following contents:

```bash
PORT="8080"
```

Run the server:

```bash
npm install
npm run dev
```

_This starts the server in non-database mode._ It will serve a simple webpage at `http://localhost:8080`.

You do _not_ need to set up a database or any interactivity on the webpage yet. Instructions for that will come later in the course!

Gautham's version of Boot.dev's Notely app

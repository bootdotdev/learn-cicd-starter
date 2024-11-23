# learn-cicd-starter (Notely)

![code coverage badge](https://github.com/DanielJacob1998/learn-cicd-starter/actions/workflows/ci.yml/badge.svg)

This repo contains the starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).

This README is for reference purposes only! Follow the instructions in the course, don't start doing all the steps here in the README.

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

*This starts the server in non-database mode.* It will serve a webpage at `http://localhost:8080`. However, you won't be able to interact with the webpage until you connect it to a MySQL database and run the migrations.

## Database Setup

This project uses a MySQL database for persistent storage. You can install MySQL locally for local development, or connect to a remote database.

Add *your* database connection string to your `.env` file. Here's an example:

```bash
DATABASE_URL="username:password@host/dbname?tls=true"
```

Once you have an empty database, you'll need to run migrations to create the schema. Make sure you have [goose](https://github.com/pressly/goose) installed:

```bash
go install github.com/pressly/goose/v3/cmd/goose@latest
```

Then run the migrations:

```bash
./scripts/migrateup.sh
```

Start the server:

```bash
go build -o notely && ./notely
```

Because the `DATABASE_URL` environment variable is set, the server will connect to the database and serve the webpage at `http://localhost:8080`. The page should be fully functional now. You can:

* Create a user (login as that user)
* Save notes
* Logout (To log in again you'll just create a new user)

*The purpose of this project is to just be a simple CRUD app that we can use to practice CI/CD. It's not meant to be a fully functional app.*

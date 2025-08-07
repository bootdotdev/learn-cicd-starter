# learn-cicd-starter (Notely)

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

*This starts the server in non-database mode.* It will serve a simple webpage at `http://localhost:8080`.

You do *not* need to set up a database or any interactivity on the webpage yet. Instructions for that will come later in the course!

Felbote's version of Boot.dev's Notely app.

A branch is (basically) a copy of your codebase. However, it's a special kind of copy that makes merging new code changes from one branch to another simple and easy.

So far, you may have been only working on the main branch, but you can create as many branches as you want, and they're a great way to keep changes that are unrelated to each other isolated and contained.

In many teams, the main branch reflects the state of the codebase that's running in production. This means that the main branch should always be stable and ready to deploy. If you want to:

Add a new feature
Fix a bug
Refactor some code
Then you should create a new branch to add those changes to. This allows you to work on those changes independently without affecting the main branch.

Assignment
Check which branch you're currently on with git branch. You'll see a list of branches, with an asterisk next to the branch you're currently on:
* main

Create a new branch called addtests. I like to name my branches after the change I'm about to make, and in this case, we're about to add tests.
git switch -c addtests

When you create a new branch, it only exists locally. Push this new branch up to GitHub:
git push origin addtests

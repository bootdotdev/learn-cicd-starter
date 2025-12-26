[![CI](https://github.com/GhostFaceInterface/learn-cicd-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/GhostFaceInterface/learn-cicd-starter/actions/workflows/ci.yml)

# learn-cicd-starter (Notely)

This repo contains the starter code for the "Notely" application for the "Learn CICD" course on [Boot.dev](https://boot.dev).


## Deployment on Google Cloud Platform (GCP)

In this course, significant work was performed to deploy the Notely app using Google Cloud Platform (GCP) services and to automate the deployment process. The steps included:

- **Dockerizing the Notely App:**  
  The application was containerized using a Dockerfile, enabling consistent builds and deployments across environments.

- **Pushing to Google Artifact Registry:**  
  The Docker image was built locally (or in CI) and pushed to Google Artifact Registry, GCP's managed container image storage solution. This allows Cloud Run to pull images securely and efficiently.

- **Deploying to Cloud Run:**  
  The container image from Artifact Registry was deployed as a Cloud Run service. Cloud Run provides a fully managed serverless platform for running containers. Understanding the distinction between a *service* (the running app) and an *image* (the app's container snapshot) was crucial.

- **Configuring Secrets with Secret Manager:**  
  Sensitive configuration, such as the database URL, was stored in GCP Secret Manager. These secrets were then referenced in the Cloud Run service's environment variables, ensuring that credentials were not hardcoded or exposed in source control.

- **IAM Role Assignment for Secrets:**  
  The Cloud Run Deployer service account was granted the `Secret Manager Secret Accessor` role, allowing the deployed service to access secrets at runtime. This required identifying the correct service account and assigning the necessary permissions.

- **Security Tab and Identity Configuration:**  
  In the Cloud Run Security tab, the deployer identity was specified to resolve permission errors related to secret access. This step was essential to ensure that Cloud Run could fetch secrets securely during deployments.

- **Verification:**  
  After deployment, the app was accessed and tested via the public Cloud Run URL, confirming that the service was running correctly and that secrets were loaded from Secret Manager.

## CI/CD Integration

Continuous Integration and Continuous Deployment (CI/CD) were implemented using GitHub Actions:

- **Automated Docker Builds and Deployment:**  
  A GitHub Actions workflow was defined to build the Docker image, push it to Google Artifact Registry, and deploy the latest image automatically to Cloud Run on every push to the main branch.

- **Database Migrations:**  
  Before deployment, the workflow ran database migrations using environment variables populated from GCP Secret Manager, ensuring the database schema was up to date.

- **Public Access Configuration:**  
  The workflow ensured that the Cloud Run service was configured to allow unauthenticated (public) access, so users could reach the app without authentication barriers.

## Summary of Accomplishments

- Successfully deployed a full-stack application using GCP services: Cloud Run, Artifact Registry, and Secret Manager.
- Established a robust CI/CD pipeline that automatically builds, tests, and deploys the application via GitHub Actions.
- Gained hands-on experience with GCP IAM roles, permissions, and secure secret management.

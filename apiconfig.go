package main

import "github.com/bootdotdev/learn-cicd-starter/internal/database"

// Minimal apiConfig so handlers with receiver *apiConfig compile.
type apiConfig struct {
	DB *database.Queries
}

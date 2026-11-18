package main

import (
	"net/http"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func (cfg *apiConfig) middlewareAuth(
	handler func(http.ResponseWriter, *http.Request, database.User),
) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		apiKey, err := auth.GetAPIKey(r)
		if err != nil {
			http.Error(w, err.Error(), http.StatusUnauthorized)
			return
		}

		// Look up the user in the database
		user, err := cfg.DB.GetUser(r.Context(), apiKey)
		if err != nil {
			http.Error(w, "invalid API key", http.StatusUnauthorized)
			return
		}

		// Call the actual handler with the authenticated user
		handler(w, r, user)
	}
}

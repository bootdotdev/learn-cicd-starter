package auth

import (
	"errors"
	"net/http"
	"strings"
)

// GetAPIKey extracts an API key from the Authorization header.
// The expected format is: "Authorization: ApiKey <key>"
func GetAPIKey(r *http.Request) (string, error) {
	const prefix = "ApiKey "

	// Get the Authorization header value
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		return "", errors.New("authorization header is missing")
	}

	// Check for the correct prefix
	if !strings.HasPrefix(authHeader, prefix) {
		return "", errors.New("authorization header must start with 'ApiKey '")
	}

	// Trim the prefix to get the actual key
	apiKey := strings.TrimPrefix(authHeader, prefix)
	apiKey = strings.TrimSpace(apiKey)

	if apiKey == "" {
		return "", errors.New("API key is missing after prefix")
	}

	return apiKey, nil
}


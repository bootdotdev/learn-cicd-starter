package auth

import (
	"errors"
	"fmt"
	"net/http"
	"strings"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")
var ErrMalformedAuthHeader = errors.New("malformed authorization header")

// GetAPIKey extracts API key from Authorization header
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", fmt.Errorf("auth error: %w", ErrNoAuthHeaderIncluded)
	}
	
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", fmt.Errorf("auth error: %w", ErrMalformedAuthHeader)
	}

	return splitAuth[1], nil
}

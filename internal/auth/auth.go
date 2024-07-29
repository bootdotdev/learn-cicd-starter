package auth

import (
	"errors"
	"net/http"
	"strings"
)

var (
	ErrNoAuthHeaderIncluded = errors.New("no authorization header included")
	ErrMalformedAuth        = errors.New("malformed authorization header")
)

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", ErrMalformedAuth
	}

	return splitAuth[1], nil
}

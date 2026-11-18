package auth

import (
	"errors"
	"net/http"
	"strings"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}

	parts := strings.Fields(authHeader)
	if len(parts) != 2 || parts[0] != "ApiKey" {
		return "", errors.New("malformed authorization header")
	}

	return parts[1], nil
}

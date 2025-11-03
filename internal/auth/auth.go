package auth

import (
	"errors"
	"net/http"
	"strings"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
    authHeader := strings.TrimSpace(headers.Get("Authorization"))
    if authHeader == "" {
        return "", ErrNoAuthHeaderIncluded
    }

    // Must start with "ApiKey " and then a non-empty key
    const prefix = "ApiKey "
    if !strings.HasPrefix(authHeader, prefix) {
        return "", errors.New("malformed authorization header")
    }

    key := strings.TrimSpace(strings.TrimPrefix(authHeader, prefix))
    if key == "" {
        return "", errors.New("malformed authorization header")
    }

    return key, nil
}

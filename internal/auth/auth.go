package auth

import (
	"errors"
	"fmt"
	"net/http"
	"strings"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")
var ErrMalformedAuthHeader = errors.New("malformed authorization header")

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	fmt.Printf("sk %v, %v, %v", splitAuth[0], splitAuth[0] == "ApiKey", len(splitAuth))
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", ErrMalformedAuthHeader
	}

	return splitAuth[1], nil
}
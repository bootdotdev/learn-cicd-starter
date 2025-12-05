package auth

import (
	"errors"
	"net/http"
)

// Error for missing header
var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

// Temporarily broken GetAPIKey for CI failure
func GetAPIKey(headers http.Header) (string, error) {
	return "BROKEN_KEY", nil
}
// CI trigger
// CI trigger comment

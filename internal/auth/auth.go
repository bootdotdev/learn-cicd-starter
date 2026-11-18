package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", errors.New("malformed authorization header")
	}

	return splitAuth[1], nil
}

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")
	got, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	want := "my-secret-key"

	if got != want {
		t.Errorf("expected %q, got %q", want, got)
	}
}

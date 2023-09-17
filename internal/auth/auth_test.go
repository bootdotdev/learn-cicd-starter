package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("Valid Authorization Header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey abcdef123456")

		apiKey, err := GetAPIKey(headers)

		if err != nil {
			t.Errorf("unexpected error: %v", err)
		}

		expectedAPIKey := "abcdef123456"
		if apiKey != expectedAPIKey {
			t.Errorf("expected API key to be '%s', got '%s'", expectedAPIKey, apiKey)
		}
	})

	t.Run("Missing Authorization Header", func(t *testing.T) {
		headers := http.Header{}

		_, err := GetAPIKey(headers)

		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("expected '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
		}
	})

	t.Run("Malformed Authorization Header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Bearer abcdef123456")

		_, err := GetAPIKey(headers)

		expectedErr := errors.New("malformed authorization header")
		if err == nil || err.Error() != expectedErr.Error() {
			t.Errorf("expected '%v', got '%v'", expectedErr, err)
		}
	})
}

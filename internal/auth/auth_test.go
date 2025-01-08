package auth_test

import (
	"net/http"
	"strings"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("returns ErrNoAuthHeaderIncluded when no Authorization header is present", func(t *testing.T) {
		headers := http.Header{}

		apiKey, err := auth.GetAPIKey(headers)
		if err == nil {
			t.Fatalf("expected an error, but got none")
		}
		if err != auth.ErrNoAuthHeaderIncluded {
			t.Errorf("expected %v, got %v", auth.ErrNoAuthHeaderIncluded, err)
		}
		if apiKey != "" {
			t.Errorf("expected empty apiKey, got %s", apiKey)
		}
	})

	t.Run("returns error when Authorization header is malformed (not enough parts)", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "MalformedValue")

		apiKey, err := auth.GetAPIKey(headers)
		if err == nil {
			t.Fatalf("expected an error, but got none")
		}
		if !strings.Contains(err.Error(), "malformed authorization header") {
			t.Errorf("expected 'malformed authorization header' error, got %v", err)
		}
		if apiKey != "" {
			t.Errorf("expected empty apiKey, got %s", apiKey)
		}
	})

	t.Run("returns error when Authorization header has invalid prefix", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Bearer SomeToken")

		apiKey, err := auth.GetAPIKey(headers)
		if err == nil {
			t.Fatalf("expected an error, but got none")
		}
		if !strings.Contains(err.Error(), "malformed authorization header") {
			t.Errorf("expected 'malformed authorization header' error, got %v", err)
		}
		if apiKey != "" {
			t.Errorf("expected empty apiKey, got %s", apiKey)
		}
	})

	t.Run("returns API key when Authorization header is valid", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey MySecretKey")

		apiKey, err := auth.GetAPIKey(headers)
		if err != nil {
			t.Fatalf("expected no error, got %v", err)
		}
		if apiKey != "MySecretKey" {
			t.Errorf("expected MySecretKey, got %s", apiKey)
		}
	})
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("extracts key from ApiKey scheme", func(t *testing.T) {
		h := http.Header{}
		h.Set("Authorization", "ApiKey my-secret-key")
		key, err := GetAPIKey(h)
		if err != nil {
			t.Fatalf("GetAPIKey: %v", err)
		}
		if key != "my-secret-key" {
			t.Errorf("key = %q, want %q", key, "my-secret-key")
		}
	})

	t.Run("missing Authorization header", func(t *testing.T) {
		h := http.Header{}
		_, err := GetAPIKey(h)
		if !errors.Is(err, ErrNoAuthHeaderIncluded) {
			t.Errorf("err = %v, want ErrNoAuthHeaderIncluded", err)
		}
	})

	t.Run("malformed Authorization header", func(t *testing.T) {
		h := http.Header{}
		h.Set("Authorization", "Bearer not-an-api-key")
		_, err := GetAPIKey(h)
		if err == nil {
			t.Fatal("expected error")
		}
		if err.Error() != "malformed authorization header" {
			t.Errorf("err = %v", err)
		}
	})
}

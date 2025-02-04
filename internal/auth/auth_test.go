package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := make(http.Header)

	key, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}

	if key != "" {
		t.Errorf("Expected empty key, got %v", key)
	}
}

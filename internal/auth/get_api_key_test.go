package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := make(http.Header)
	header.Set("Authorization", "ApiKey testKey")

	key, err := GetAPIKey(header)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if key != "testKey" {
		t.Errorf("expected key %q, got %q", "testKey", key)
	}
}

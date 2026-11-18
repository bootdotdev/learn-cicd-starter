package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "ApiKey testkey")

	key, err := GetAPIKey(h)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if key != "testkey" {
		t.Fatalf("expected testkey, got %s", key)
	}
}

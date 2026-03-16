package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyWithValidKey(t *testing.T) {
	headers := http.Header{"Authorization": []string{"ApiKey test-key-123"}}
	key, err := GetAPIKey(headers)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if key != "test-key-123" {
		t.Errorf("expected key 'test-key-123', got %q", key)
	}
}

func TestGetAPIKeyWithMissingHeader(t *testing.T) {
	headers := http.Header{}
	key, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}

	if key != "" {
		t.Errorf("expected empty key, got %q", key)
	}
}

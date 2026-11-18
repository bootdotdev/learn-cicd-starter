package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeySuccess(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if apiKey != "my-secret-key" {
		t.Fatalf("expected api key %q, got %q", "my-secret-key", apiKey)
	}
}

func TestGetAPIKeyNoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected an error, got nil")
	}

	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

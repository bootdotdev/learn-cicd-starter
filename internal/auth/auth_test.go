package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey abc123xyz")

	apiKey, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("Expected no error, got: %v", err)
	}
	if apiKey != "abc123xyz" {
		t.Errorf("Expected API key 'abc123xyz', got: %s", apiKey)
	}
}

func TestGetAPIKey_MissingAuthHeader(t *testing.T) {
	headers := http.Header{}

	apiKey, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got: %v", err)
	}
	if apiKey != "" {
		t.Errorf("Expected empty API key, got: %s", apiKey)
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyNoAuthHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Errorf("Expected an error when no Authorization header is included, got nil")
	}
}

func TestGetAPIKeyMalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "MalformedApiKey")
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Errorf("Expected an error when Authorization header is malformed, got nil")
	}
}

func TestGetAPIKeySuccess(t *testing.T) {
	expectedApiKey := "test-api-key"
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey "+expectedApiKey)
	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Did not expect an error, got %v", err)
	}
	if apiKey != expectedApiKey {
		t.Errorf("Expected API key to be %s, got %s", expectedApiKey, apiKey)
	}
}

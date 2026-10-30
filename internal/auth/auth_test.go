package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey test_api_key_123")

	apiKey, err := auth.GetAPIKey(headers)
	if err != nil {
		t.Errorf("Expected no error, got: %v", err)
	}
	if apiKey != "test_api_key_123" {
		t.Errorf("Expected apiKey to be 'test_api_key_123', got: %s", apiKey)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := auth.GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error when no Authorization header is present")
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer token_incorrect")

	_, err := auth.GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error when Authorization header is malformed")
	}
}

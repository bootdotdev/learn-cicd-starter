package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyHappyPath(t *testing.T) {
	headers := http.Header{
		"Authorization": []string{"ApiKey key123"},
	}

	expectedKey := "key123"
	expectedError := error(nil)

	apiKey, err := GetAPIKey(headers)

	// Check API Key
	if apiKey != expectedKey {
		t.Errorf("expected key %s, got %s", expectedKey, apiKey)
	}

	// Check error
	if err != expectedError {
		t.Errorf("expected no error, got %v", err)
	}
}


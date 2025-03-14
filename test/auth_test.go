package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	expectedAPIKey := "valid_api_key"
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey "+expectedAPIKey)

	apiKey, err := auth.GetAPIKey(headers)

	if err != nil {
		t.Errorf("Error getting API key from valid header: %v", err)
	}
	if apiKey != expectedAPIKey {
		t.Errorf("Incorrect API key extracted: got %s, want %s", apiKey, expectedAPIKey)
	}
}

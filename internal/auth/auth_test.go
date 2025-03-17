package auth // Declare your package here

import (
	"net/http"
	"testing"
	// Import any other required packages
)

func TestGetAPIKey_ValidAuthorization(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-token")

	apiKey, err := GetAPIKey(headers)
	expectedKey := "my-secret-token"

	if err != nil {
		t.Fatalf("Expected no error, but got %v", err)
	}

	if apiKey != expectedKey {
		t.Errorf("expected %s, but got %s", expectedKey, apiKey)

	}
}

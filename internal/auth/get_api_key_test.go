package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey test1234567890")

	apiKey, err := GetAPIKey(header)
	if err != nil {
		t.Fatalf("Failed to get API key: %v", err)
	}
	if apiKey != "test" {
		t.Fatalf("Expected API key to be 'test', got '%s'", apiKey)
	}

}

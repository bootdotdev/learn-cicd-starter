package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 12345")
	apiKey, err := GetAPIKey(headers)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if apiKey != "12345" {
		t.Fatalf("expected apiKey to be '12345', got %v", apiKey)
	}

}

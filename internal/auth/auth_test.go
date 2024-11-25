package auth

import (
	"net/http"
	"testing"
)

func TestExtractAPIKeyWithCorrectHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	apiKey, err := GetAPIKey(headers)

	if err != nil {
		t.Fatalf("expected no errors, got %v", err)
	}
	expected := "my-secret-key"
	if apiKey != expected {
		t.Fatalf("expected %v errors, got %v", expected, apiKey)
	}
}
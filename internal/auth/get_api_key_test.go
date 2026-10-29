package auth

import (
	"net/http"
	"testing"
)

// Test 1: Standard valid API key
func TestGetAPIKey_ValidStandardKey(t *testing.T) {
	headers := http.Header{}
	expectedKey := "prod_live_abc123xyz"
	headers.Set("Authorization", "ApiKey "+expectedKey)

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got: %v", err)
	}

	if apiKey != expectedKey {
		t.Errorf("expected key %q, got %q", expectedKey, apiKey)
	}
}

// Test 2: Valid key containing special characters (e.g., base64 or hyphenated UUID)
func TestGetAPIKey_ValidKeyWithSpecialCharacters(t *testing.T) {
	headers := http.Header{}
	expectedKey := "sk_test_51Mz-q8==.uuid-99a0-4ffb"
	headers.Set("Authorization", "ApiKey "+expectedKey)

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got: %v", err)
	}

	if apiKey != expectedKey {
		t.Errorf("expected key %q, got %q", expectedKey, apiKey)
	}
}

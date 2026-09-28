package auth

import (
	"net/http"
	"testing"
)

func TestAPIkey(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	headers := req.Header
	headers.Add("Authorization", "ApiKey 12345")
	APIKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("TestGetAPIKey failed: unexpected error: %v", err)
		return
	}

	expectedAPIKey := "12345"
	if APIKey != expectedAPIKey {
		t.Errorf("TestGetAPIKey failed: expected '%s', got '%s'", expectedAPIKey, APIKey)
	}
}

func TestAPIkeyBadToken(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	headers := req.Header
	headers.Add("Authorization", "Bearer Token 234")
	APIKey, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("TestGetAPIKeyBadToken failed: expected error, got none: %v", err)
		return
	}

	if err != ErrMalformedAuthHeader {
		t.Fatalf("TestGetAPIKeyBadToken failed: expected error '%v', but got '%v'", ErrMalformedAuthHeader, err)
		return
	}

	expectedAPIKey := ""
	if APIKey != expectedAPIKey {
		t.Errorf("TestGetAPIKeyBadToken failed: expected APIKey to be empty, but got: '%s'", APIKey)
	}
}

func TestAPIkeyEmpty(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	headers := req.Header
	headers.Add("Authorization", "")
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("Expected an error for empty string, got nil")
		return
	}

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected error ErrNoAuthHeaderIncluded, got %v", err)
	}

	apiKey := ""
	if apiKey != "" {
		t.Errorf("Expected empty APIKey on error, got %s", apiKey)
	}
}

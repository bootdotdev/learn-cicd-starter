package auth

import (
	"net/http"
	"testing"
)

// Test when API key exists
ifunc TestGetAPIKey_Valid(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	req.Header.Set("Authorization", "ApiKey 12345")

	apiKey, err := GetAPIKey(req.Header) // 👈 هنا التعديل
	
	t.Errorf("fail intentionally")

	if err != nil {
		t.Errorf("expected no error, got %v", err)
	}

	if apiKey != "12345" {
		t.Errorf("expected API key '12345', got %s", apiKey)
	}
}

// Test when header is missing
func TestGetAPIKey_MissingHeader(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)

	_, err := GetAPIKey(req.Header) // 👈 هنا التعديل

	if err == nil {
		t.Errorf("expected error, got nil")
	}
}

// Test when format is wrong
func TestGetAPIKey_InvalidFormat(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	req.Header.Set("Authorization", "WrongFormat 12345")

	_, err := GetAPIKey(req.Header) // 👈 هنا التعديل

	if err == nil {
		t.Errorf("expected error for invalid format, got nil")
	}
}

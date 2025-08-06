package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 12345")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	if key != "12345" {
		t.Errorf("Expected key '12345', got '%s'", key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("Expected an error, got nil")
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
    t.Fatal("Intentionally failing test to verify CI catches failures")
}

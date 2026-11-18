package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey testkey123") //  Use ApiKey

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("GetAPIKey() returned unexpected error: %v", err)
	}

	want := "testkey123"
	if got != want {
		t.Errorf("GetAPIKey() = %q; want %q", got, want)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("Expected error for missing header, got nil")
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer testkey123") // intentionally wrong

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("Expected error for malformed header, got nil")
	}
}

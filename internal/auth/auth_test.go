package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey abc123")
	//headers.Set("Authorization", "abc123")

	got, err := GetAPIKey(headers)
	want := "abc123"
	//want := "wrongkey"

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if got != want {
		t.Errorf("Expected API key %q, got %q", want, got)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer abc123")

	_, err := GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("Expected malformed header error, got %v", err)
	}
}

func TestGetAPIKey_EmptyKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey ")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("Expected no error for empty key, got %v", err)
	}
	if got != "" {
		t.Errorf("Expected empty string, got %q", got)
	}
}

/*
func TestGetAPIKey_ExtraSpaces(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey    abc123")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if got != "abc123" {
		t.Errorf("Expected 'abc123', got %q", got)
	}
}


func TestGetAPIKey_MultipleParts(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey abc123 extra")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if got != "abc123" {
		t.Errorf("Expected 'abc123', got %q", got)
	}
}
*/

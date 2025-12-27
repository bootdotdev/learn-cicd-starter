package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected: %v, got: %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer sometoken")

	_, err := GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Fatalf("expected: malformed authorization header, got: %v", err)
	}
}
func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	got, err := GetAPIKey(headers)
	want := "my-secret-key"

	if err != nil {
		t.Fatalf("expected no error, got: %v", err)
	}
	if got != want {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

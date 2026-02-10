package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if apiKey != "my-secret-key" {
		t.Fatalf("expected 'my-secret-key', got '%s'", apiKey)
	}
}

func TestGetAPIKey_NoAuthorizationHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error, got nil")
	}

	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_MalformedHeader_MissingKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey")

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

func TestGetAPIKey_MalformedHeader_WrongPrefix(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer my-secret-key")

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

func TestGetAPIKey_MalformedHeader_EmptyValue(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey ")

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

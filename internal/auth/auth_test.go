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
		t.Fatalf("expected no error, got: %v", err)
	}
	if apiKey != "my-secret-key" {
		t.Fatalf("expected 'my-secret-key', got: %s", apiKey)
	}
}

func TestGetAPIKey_NoAuthHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if err == nil {
		t.Fatal("expected an error, got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected error '%v', got: %v", ErrNoAuthHeaderIncluded, err)
	}
}

// func TestFail(t *testing.T) {
// 	t.Fail()
// }

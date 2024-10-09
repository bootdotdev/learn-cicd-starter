package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyNoAuth(t *testing.T) {
	headers := http.Header{}
	headers.Add("Content-Type", "application/json")
	result, err := GetAPIKey(headers)
	if result != "" {
		t.Fatalf("Unexpected return: %s", result)
	}
	if err == nil {
		t.Fatal("No error for headers without Authorization")
	}
}

func TestGetAPIKeyInvalidAuth(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "")
	result, err := GetAPIKey(headers)
	if result != "" {
		t.Fatalf("Unexpected return: %s", result)
	}
	if err == nil {
		t.Fatal("No error for headers without Authorization")
	}
}

func TestGetAPIKeyValidAuth(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey 213234asdas4")
	result, err := GetAPIKey(headers)
	if result != "" {
		t.Fatalf("Unexpected return: %s", result)
	}
	if err != nil {
		t.Fatalf("Unexpected error for valid auth header format: %s", err)
	}
}

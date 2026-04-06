package auth

import (
	"testing"
	"net/http"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey rest-api-key")
	got, err:= GetAPIKey(headers)
	if got != "test-api-key" {
		t.Error("Expected API key, got empty string")
	} 
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if got == "my-api-key" {
		t.Error("Expected API key, got a wrong string")
	}
}

func TestGetAPIKeyNoHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

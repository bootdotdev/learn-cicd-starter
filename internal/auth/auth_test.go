package auth

import (
	"errors"
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey_NoAuthHeader(t *testing.T) {
	headers := http.Header{}

	apiKey, err := GetAPIKey(headers)

	if apiKey != "" {
		t.Errorf("Expected no API key, got %s", apiKey)
	}

	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_EmptyAuthHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "")

	apiKey, err := GetAPIKey(headers)
	fmt.Print(GetAPIKey(headers))

	if apiKey != "" {
		t.Errorf("Expected no API key, got %s", apiKey)
	}

	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_MalformedAuthHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "InvalidFormat")

	_, err := GetAPIKey(headers)

	if err == nil {
		t.Error("Expected error for malformed authorization header, got nil")
	}
}

func TestGetAPIKey_CorrectHeader(t *testing.T) {
	expectedApiKey := "testkey123"
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey "+expectedApiKey)

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Did not expect an error, got %v", err)
	}

	if apiKey != expectedApiKey {
		t.Errorf("Expected API key %s, got %s", expectedApiKey, apiKey)
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyValidHeader(t *testing.T) {
	header := http.Header{}
	header.Add("Authorization", "ApiKey my-api-key")

	apiKey, err := GetAPIKey(header)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	expectedAPIKey := "my-api-key"
	if apiKey != expectedAPIKey {
		t.Errorf("Expected API key to be %s, but got %s", expectedAPIKey, apiKey)
	}
}

func TestGetAPIKeyNoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if err == nil || err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded error, got %v", err)
	}
}

func TestGetAPIKeyMalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "Bearer my-token")

	_, err := GetAPIKey(headers)

	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("Expected 'malformed authorization header' error, got %v", err)
	}
}

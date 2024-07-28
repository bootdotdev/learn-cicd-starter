package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey_AuthorizationHeaderMissing(t *testing.T) {
	// Create a request with an empty header
	headers := http.Header{}

	// Call the GetAPIKey function
	apiKey, err := auth.GetAPIKey(headers)

	// Check if the error is as expected
	if err != auth.ErrNoAuthHeaderIncluded {
		t.Errorf("expected error: %v, got: %v", auth.ErrNoAuthHeaderIncluded, err)
	}

	// Check if apiKey is an empty string
	if apiKey != "" {
		t.Errorf("expected apiKey to be empty, got: %v", apiKey)
	}
}

func TestGetAPIKey_MalformedAuthorizationHeader(t *testing.T) {
	// Test case where header doesn't start with "ApiKey"
	headers1 := http.Header{}
	headers1.Set("Authorization", "Bearer someapikey")

	// Call the GetAPIKey function
	_, err1 := auth.GetAPIKey(headers1)

	// Check if the error is as expected
	if err1 == nil || err1.Error() != "malformed authorization header" {
		t.Errorf("expected error: 'malformed authorization header', got: %v", err1)
	}

	// Test case where header is not correctly spaced
	headers2 := http.Header{}
	headers2.Set("Authorization", "ApiKeysomeapikey")

	// Call the GetAPIKey function
	_, err2 := auth.GetAPIKey(headers2)

	// Check if the error is as expected
	if err2 == nil || err2.Error() != "malformed authorization header" {
		t.Errorf("expected error: 'malformed authorization header', got: %v", err2)
	}
}
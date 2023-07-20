package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	// Case 1: No authorization header included
	headers := http.Header{}
	key, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
	if key != "" {
		t.Errorf("expected key to be empty, got %v", key)
	}

	// Case 2: Malformed authorization header
	headers.Add("Authorization", "ApiKey")

	_, err = GetAPIKey(headers)

	var errMessage = ErrMalFormed

	if err != ErrMalFormed {
		t.Errorf("expected %v , got %v", errMessage, err)
	}

	// Case 3: Valid authorization header
	headers.Del("Authorization")
	headers.Add("Authorization", "ApiKey my-api-key")
	key, err = GetAPIKey(headers)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if key != "my-api-key" {
		t.Errorf("expected key to be 'my-api-key', got %v", key)
	}

}

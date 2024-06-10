package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test case 1: No Authorization header
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
	}

	// Test case 2: Malformed Authorization header - missing ApiKey
	headers.Set("Authorization", "Bearer somekey")
	_, err = GetAPIKey(headers)
	expectedErr := errors.New("malformed authorization header")
	if err == nil || err.Error() != expectedErr.Error() {
		t.Errorf("expected error %v, got %v", expectedErr, err)
	}

	// Test case 3: Malformed Authorization header - missing key
	headers.Set("Authorization", "ApiKey")
	_, err = GetAPIKey(headers)
	if err == nil || err.Error() != expectedErr.Error() {
		t.Errorf("expected error %v, got %v", expectedErr, err)
	}

	// Test case 4: Correct Authorization header
	headers.Set("Authorization", "ApiKey somekey")
	key, err := GetAPIKey(headers)
	if key != "somekey" {
		t.Errorf("expected key 'somekey', got %v", key)
	}
	if err != nil {
		t.Errorf("expected no error, got %v", err)
	}
}

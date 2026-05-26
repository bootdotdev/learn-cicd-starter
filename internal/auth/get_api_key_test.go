package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKeyPresent(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey key-1234")
	key, err := GetAPIKey(header)
	if key != "key-1234" || err != nil {
		t.Errorf("Want authorization key to be %q and error to be nil but got %q and %v", "key-1234", key, err)
	}
}

func TestGetApiKeyAbsent(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "Auth")
	_, err := GetAPIKey(header)
	if err.Error() != "malformed authorization header" {
		t.Errorf("Expected error %q but got %q", "malformed authorization header", err.Error())
	}
}

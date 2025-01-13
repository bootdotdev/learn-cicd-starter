package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKeyPass(t *testing.T) {
	header := http.Header{}
	keyVal := "ValidKey"
	header.Add("Authorization", fmt.Sprintf("ApiKey %s", keyVal))

	key, err := GetAPIKey(header)
	if err != nil {
		t.Errorf("GetAPIKey unexpected error for expected valid key format: %v", err)
	}

	if key != keyVal {
		t.Errorf("Expected key value [%v], but received [%v]", keyVal, key)
	}
}

func TestGetAPIKeyEmptyHeader(t *testing.T) {
	header := http.Header{}

	_, err := GetAPIKey(header)
	if err == nil {
		t.Error("GetAPIKey expected the function to throw error for empty header")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("GetAPIKey unexpected error from empty header: %v", err)
	}
}

func TestGetAPIKeyInvalidKey(t *testing.T) {
	header := http.Header{}
	keyVal := "InvalidKey"
	header.Add("Authorization", fmt.Sprintf("NotApiKey %s", keyVal))

	_, err := GetAPIKey(header)
	if err == nil {
		t.Error("GetAPIKey expected the function to throw error for malformed key")
	}

	if err == ErrNoAuthHeaderIncluded {
		t.Errorf("GetAPIKey got unexpected error for auth header not included: %v", err)
	}
}

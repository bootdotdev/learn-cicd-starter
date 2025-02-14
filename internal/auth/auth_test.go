package auth

import (
	"net/http"
	"testing"
)

func TestEmptyHeader(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "")
	if _, err := GetAPIKey(header); err != ErrNoAuthHeaderIncluded {
		t.Error("Expected empty header error, found none")
	}
}

func TestMalformedHeader(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "something wrong")
	if _, err := GetAPIKey(header); err == nil {
		t.Error("Expected malformed authorization header, got none")
	}

	header.Set("Authorization", "ApiKey")
	if _, err := GetAPIKey(header); err == nil {
		t.Error("Expected malformed authorization header, got none")
	}
}

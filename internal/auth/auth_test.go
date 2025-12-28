package auth

import (
	"net/http"
	"testing"
)

func TestMain(t *testing.T) {
	headers := http.Header{}

	// Invalid No auth header
	v, err := GetAPIKey(headers)
	if err == nil {
		t.Error("Expected Error")
	} else if v != "" {
		t.Error("Expected nil value, received", v)
	}

	// Valid API key
	headers.Set("Authorization", "ApiKey test_api_key")
	v, err = GetAPIKey(headers)
	if err != nil {
		t.Error("Expected no Error, received", err)
	} else if v != "test_api_key" {
		t.Error("Mismatched key value, received", v)
	}
	headers.Del("Authorization")

	// Invalid API Key
	headers.Set("Authorization", "ApiKey")
	v, err = GetAPIKey(headers)
	if err == nil {
		t.Error("Expected Error")
	} else if v != "" {
		t.Error("Expected nil value, received", v)
	}
	headers.Del("Authorization")

}

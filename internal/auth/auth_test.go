package auth

import (
	"net/http"
	"testing"
)

// TestGetAPIKeyEmpty calls auth.GetAPIKey with empty authorization
func TestGetAPIKeyNil(t *testing.T) {
	header := http.Header{}

	api, err := GetAPIKey(header)
	if err == nil || api != "" {
		t.Fatalf("GetAPIKey supposed to return no auth header err vs. %v, and empty string vs %s", err, api)
	}
}

// TestGetAPIKeyWrong calls auth.GetAPIKey with null key
func TestGetAPIKeyEmpty(t *testing.T) {
	header := http.Header{}

	headerKey := "Authorization"
	apiKey := ""

	header.Set(headerKey, apiKey)

	api, err := GetAPIKey(header)
	if err == nil || api != "" {
		t.Fatalf("GetAPIKey supposed to return malformed auth err vs. %v, and empty string vs %s", err, api)
	}
}

// TestGetAPIKeyWrong calls auth.GetAPIKey with null key
func TestGetAPIKeyWrong(t *testing.T) {
	header := http.Header{}

	headerKey := "Authorization"
	apiKey := "testing123333"

	header.Set(headerKey, apiKey)

	api, err := GetAPIKey(header)
	if err == nil || api != "" {
		t.Fatalf("GetAPIKey supposed to return malformed auth err vs. %v, and \"\" vs %q", err, api)
	}
}

// TestGetAPIKey successfully calls auth.GetAPIKey
func TestGetAPIKey(t *testing.T) {
	header := http.Header{}

	headerKey := "Authorization"
	apiKey := "ApiKey testing123333"

	header.Set(headerKey, apiKey)

	api, err := GetAPIKey(header)
	if err != nil || api != "testing123333" {
		t.Fatalf("GetAPIKey supposed to return nil err vs. %v, and \"testing123333\" vs %q", err, api)
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	req, err := http.NewRequest("GET", "https://api.github.com", nil)
	if err != nil {
		t.Error(err)
	}
	req.Header.Set("Authorization", "ApiKey 1234567890")

	apiKey, err := GetAPIKey(req.Header)
	if err != nil {
		t.Error(err)
	}

	if apiKey != "1234567890" {
		t.Error("API key is not equal")
	}

	req, err = http.NewRequest("GET", "https://api.github.com", nil)
	if err != nil {
		t.Error(err)
	}
	req.Header.Set("Auth", "ApiKey 1234567890")
	_, err = GetAPIKey(req.Header)
	if err == nil {
		t.Error("Error should be returned")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Error("Error should be ErrNoAuthHeaderIncluded")
	}

	req, err = http.NewRequest("GET", "https://api.github.com", nil)
	if err != nil {
		t.Error(err)
	}
	req.Header.Set("Authorization", "api-key 1234567890")

	_, err = GetAPIKey(req.Header)
	if err.Error() != "malformed authorization header" {
		t.Error(err)
	}

}

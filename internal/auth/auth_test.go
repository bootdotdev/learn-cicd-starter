package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey thisismyapikey")
	apiKey, err := GetAPIKey(header)
	if err != nil {
		t.Error(err)
	}
	if apiKey != "thisismyapikey" {
		t.Error("API key not parsed correctly")
	}
}

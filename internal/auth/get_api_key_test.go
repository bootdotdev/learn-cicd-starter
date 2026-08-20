package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{
		"Authorization": {"ApiKey 1234567890"},
	}
	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("error should be nil, got %v", err)
	}
	if apiKey != "1234567890" {
		t.Errorf("API key should be 1234567890, got %v", apiKey)
	}
}

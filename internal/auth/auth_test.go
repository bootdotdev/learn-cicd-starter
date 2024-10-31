package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	myHeaders := http.Header{}
	myHeaders.Set("Authorization", "ApiKey 1234567890")

	apiKey, err := GetAPIKey(myHeaders)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if apiKey != "1234567890" {
		t.Errorf("expected api key to be 1234567890, got %s", apiKey)
	}
}

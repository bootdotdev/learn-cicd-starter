package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey 1234567890")
	apiKey, err := GetAPIKey(headers)
	if apiKey != "1234567890" || err != nil {
		t.Fatalf(`GetApiKey(headers) = %q, %v, want match for %#q, nil`, apiKey, err, "1234567890")
	}
}

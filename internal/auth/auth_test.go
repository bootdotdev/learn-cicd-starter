package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	headers := http.Header{}
	headers.Set("Authorization", "ApiKey validApiKey123")

	expectedOut := "validApiKey123"
	actualOut, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("Got error: %v", err)
	}
	if expectedOut != actualOut {
		t.Errorf("expected api key: %s, got actual api key: %s", expectedOut, actualOut)
	}

}

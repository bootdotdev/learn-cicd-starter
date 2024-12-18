package auth

import (
	"net/http"
	"testing"
)

func TestSplit(t *testing.T) {
	header := http.Header{}
	header.Add("Authorization", "ApiKey some_token")

	apiKey, err := GetAPIKey(header)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	expectedAPIKey := "some_token"
	if apiKey != expectedAPIKey {
		t.Fatalf("expected: %s, got: %s", expectedAPIKey, apiKey)
	}
}

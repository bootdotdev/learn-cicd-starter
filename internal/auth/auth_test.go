package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{}
	header.Add("Authorization", "ApiKey my-secret")

	apiKey, err := GetAPIKey(header)
	if err != nil {
		t.Fatal("expected no error, got:", err)
	}

	if apiKey != "my-secret" {
		t.Fatalf("expected api key to be: my-secret, got: %v", apiKey)
	}
}

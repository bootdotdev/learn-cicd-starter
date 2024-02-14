package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	testApiKey := "reallysecureapikey"
	testHeader := http.Header{}
	testHeader.Set("Authorization", fmt.Sprintf("ApiKey %s", testApiKey))

	foundApiKey, err := GetAPIKey(testHeader)
	if err != nil {
		t.Fatalf("Error getting API key from header: %s", err)
	}
	if foundApiKey != testApiKey {
		t.Fatalf("Expected key: %s. Actual key: %s", testApiKey, foundApiKey)
	}
}

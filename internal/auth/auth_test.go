package auth

import (
	"fmt"
	"net/http"
	"testing"
)

// Test GetAPIKey -
func TestGetAPIKey(t *testing.T) {
	header := http.Header{}
	header.Add("Authorization", "ApiKey 1234")
	got, err := GetAPIKey(header)
	if err != nil || got != "1234" {
		t.Fatal(fmt.Printf(`GetApiKey("Authorization: ApiKey 1234") = %q, %v, want "1234", error`, got, err))
	}
}

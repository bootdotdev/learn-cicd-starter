package auth

import (
	"net/http"
	"testing"
)

func TestAPI(t *testing.T) {

	testKey := "ThisIsAKey"

	header := http.Header{}
	header.Add("Content-Type", "application/json")
	header.Set("Authorization", "ApiKey "+testKey)

	key, err := GetAPIKey(header)
	if err != nil {
		t.Fatalf("error: could not get api key: %v", err)
	}
	if key == "ThisIsAKey" {
		return
	} else {
		t.Fatalf("error: expected %v, got %v, : %v", testKey, key, err)
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	someHTTPHeader := http.Header{}
	apiKey := "my-random-api-key"
	someHTTPHeader.Add("Authorization", "ApiKey my-random-api-key")

	apiKeyFromFunction, err := GetAPIKey(someHTTPHeader)

	if err != nil {
		t.Errorf(err.Error())
	}

	if apiKeyFromFunction != apiKey {
		t.Errorf("Expected %s, got %s", apiKey, apiKeyFromFunction)
	}
}

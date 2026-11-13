package auth

import (
	"net/http"
	"testing"
)

// TestHelloName calls greetings.Hello with a name, checking
// for a valid return value.
func TestGetApiKey(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey <KEY>")

	apiKey, err := GetAPIKey(header)
	if apiKey != "<KEY>" || err != nil {
		t.Errorf("Expected <KEY> but got %s", apiKey)
	}
}

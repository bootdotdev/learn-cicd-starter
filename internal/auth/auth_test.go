package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
    headers := &http.Header{}
    (*headers).Add("Authorization", "ApiKey thisisakey")

    key, APIKeyErr := GetAPIKey(*headers)
    if APIKeyErr != nil {
        t.Fatalf("Encountered error: %s.", APIKeyErr)
    }

    if key != "thisisakey" {
        t.Fatalf("Fetched key was not the expected string: 'thisisakey'. Instead it was: %s.", key)
    }
}

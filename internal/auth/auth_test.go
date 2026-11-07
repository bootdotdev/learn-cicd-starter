package auth

import (
	"net/http"
	"strings"
	"testing"
)

func Test(t *testing.T) {
	expectedKey := "1a2b3c4d5e6f"

	headers := make(http.Header)

	headers.Add("Authorization", strings.Join([]string{"ApiKey", expectedKey}, " "))

	actualKey, err := GetAPIKey(headers)

	if actualKey != expectedKey {
		t.Errorf("the key %v passed in the header is different from key %v returned on parsing.", expectedKey, actualKey)
	}

	if err != nil {
		t.Errorf("Expected no error but received %v", err)
	}

}

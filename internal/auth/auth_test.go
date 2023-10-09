package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	goodHeader := http.Header(map[string][]string{})
	goodHeader.Add("Authorization", "ApiKey 123456789")

	if _, err := GetAPIKey(goodHeader); err != nil {
		t.Errorf("expected to find key")
	}

	missingPrefix := http.Header(map[string][]string{})
	missingPrefix.Add("Authorization", "123456789")

	if _, err := GetAPIKey(missingPrefix); err == nil {
		t.Errorf("missing prefix: expected malformed error")
	}

	misLabeledPrefix := http.Header(map[string][]string{})
	misLabeledPrefix.Add("Authorization", "Key 123456789")

	if _, err := GetAPIKey(missingPrefix); err == nil {
		t.Errorf("mislabeled prefix: expected malformed error")
	}

}

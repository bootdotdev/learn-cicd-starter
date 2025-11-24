package auth

import (
	"net/http"
	"testing"
)

func TestError(t *testing.T) {
	expected := "no authorization header included"
	actual := ErrNoAuthHeaderIncluded.Error()
	if actual != expected {
		t.Errorf("expected %s, got %s", expected, actual)
	}
}

func TestGetAPIKey_whenNoHeaderIsSet(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected %s, got %s", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_whenHeaderIsSet(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 1234567890")
	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("unexpected error: %s", err)
	}
	if apiKey != "1234567890" {
		t.Errorf("expected %s, got %s", "1234567890", apiKey)
	}
}

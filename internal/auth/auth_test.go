package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyMissingHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected error '%v', but got '%v'", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKeyMalformedHeader(t *testing.T) {
	headers := http.Header{
		"Authorization": []string{"MalformedToken"},
	}
	_, err := GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("Expected error 'malformed authorization header', but got '%v'", err)
	}
}

func TestGetAPIKeyValidHeader(t *testing.T) {
	apiKey := "12345"
	headers := http.Header{
		"Authorization": []string{"ApiKey " + apiKey},
	}
	got, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Did not expect an error, but got '%v'", err)
	}
	if got != apiKey {
		t.Errorf("Expected '%s', but got '%s'", apiKey, got)
	}
}

func TestGetAPIKeyUnsupportedScheme(t *testing.T) {
	headers := http.Header{
		"Authorization": []string{"Unsupported "},
	}
	_, err := GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("Expected error 'malformed authorization header', but got '%v'", err)
	}
}

func TestGetAPIKeyOnlyPrefix(t *testing.T) {
	headers := http.Header{
		"Authorization": []string{"ApiKey "},
	}
	token, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Did not expect an error, but got '%v'", err)
	}
	if token != "" {
		t.Errorf("Expected an empty token, but got '%s'", token)
	}
}

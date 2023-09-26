package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyBlank(t *testing.T) {
	_, err := GetAPIKey(http.Header{})

	if err == nil {
		t.Fatalf("expected function to fail with a blank header")
	}

	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected no auth header error")
	}
}

func TestGetAPIKeyBadHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "BadKey 123")

	_, err := GetAPIKey(headers)

	if err == nil {
		t.Fatalf("expected function to fail with a bad key")
	}

	if err.Error() != "malformed authorization header" {
		t.Fatalf("expected malformed auth header response")
	}
}

func TestGetAPIKeyBadLength(t *testing.T) {
	var headers http.Header = http.Header{}

	headers.Set("Authorization", "g")

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("expected function to fail with a bad header")
	}

	if err.Error() != "malformed authorization header" {
		t.Fatalf("expected malformed auth header response")
	}
}

func TestGetAPIKeyPos(t *testing.T) {
	var headers http.Header = http.Header{}

	headers.Set("Authorization", "ApiKey 12345")

	auth, err := GetAPIKey(headers)

	if err != nil {
		t.Fatalf("expected passing case")
	}

	if auth != "12345" {
		t.Fatalf("expected api key 12345")
	}
}

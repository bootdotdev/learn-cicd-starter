package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey customValue")
	value, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("error getting api key: %v", err)
	}
	if value != "customValue" {
		t.Fatalf("invalid api key value: %v", value)
	}
}

func TestGetAPIKeyFails(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "")
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("did not throw expected error")
	}
	if err.Error() != "no authorization header included" {
		t.Fatalf("invalid err: %v", err)
	}
}

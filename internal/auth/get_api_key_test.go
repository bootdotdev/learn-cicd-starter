package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 123456")
	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("error")
	}
	want := "123456"
	if got != want {
		t.Fatalf("wrong key")
	}
}

func TestGetAPIKeyNoHeader(t *testing.T) {
	headers := http.Header{}
	got, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("error")
	}
	if got != "" {
		t.Fatalf("wrong key")
	}
}

func TestGetAPIKeyMalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKeyy 123456")
	got, err := GetAPIKey(headers)
	if err != ErrMalformedHeaderIncluded {
		t.Fatalf("wrong error")
	}
	if got != "" {
		t.Fatalf("wrong key")
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 12345")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != "12345" {
		t.Fatalf("expected key %q, got %q", "12345", got)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got: %v", err)
	}
}

func TestGetAPIKey_MalformedHeaders(t *testing.T) {
	cases := []struct {
		name   string
		header string
	}{
		{"WrongScheme", "Bearer 12345"},
		{"MissingKey", "ApiKey"},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			h := http.Header{}
			h.Set("Authorization", tc.header)

			_, err := GetAPIKey(h)
			if err == nil {
				t.Fatalf("expected error for header %q, got nil", tc.header)
			}
			if err.Error() != "malformed authorization header" {
				t.Fatalf("expected malformed authorization header error, got %v", err)
			}
		})
	}
}

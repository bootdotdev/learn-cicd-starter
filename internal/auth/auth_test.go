package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey abc123")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if apiKey != "abc123" {
		t.Fatalf("expected api key %q, got %q", "abc123", apiKey)
	}
}

func TestGetAPIKey_Errors(t *testing.T) {
	tests := []struct {
		name      string
		authValue string
		wantNoHdr bool
	}{
		{name: "missing authorization header", authValue: "", wantNoHdr: true},
		{name: "wrong authorization prefix", authValue: "Bearer abc123", wantNoHdr: false},
		{name: "missing api key value", authValue: "ApiKey", wantNoHdr: false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			headers := http.Header{}
			if tc.authValue != "" {
				headers.Set("Authorization", tc.authValue)
			}

			_, err := GetAPIKey(headers)
			if err == nil {
				t.Fatal("expected error, got nil")
			}

			if tc.wantNoHdr && !errors.Is(err, ErrNoAuthHeaderIncluded) {
				t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
			}

			if !tc.wantNoHdr && errors.Is(err, ErrNoAuthHeaderIncluded) {
				t.Fatalf("expected malformed authorization header error, got %v", err)
			}
		})
	}
}

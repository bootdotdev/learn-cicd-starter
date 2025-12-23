package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headerValue string
		wantKey     string
		wantErr     error
	}{
		{
			name:        "missing authorization header",
			headerValue: "",
			wantErr:     ErrNoAuthHeaderIncluded,
		},
		{
			name:        "malformed header",
			headerValue: "ApiKey",
			wantErr:     ErrMalformedAuthHeader,
		},
		{
			name:        "wrong auth scheme",
			headerValue: "Bearer token",
			wantErr:     ErrMalformedAuthHeader,
		},
		{
			name:        "valid api key",
			headerValue: "ApiKey my-key",
			wantKey:     "my-key",
			wantErr:     nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.headerValue != "" {
				headers.Set("Authorization", tt.headerValue)
			}

			key, err := GetAPIKey(headers)

			if tt.wantErr != nil {
				if err != tt.wantErr {
					t.Fatalf("expected error %v, got %v", tt.wantErr, err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if key != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, key)
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		header    string
		wantKey   string
		wantError error
	}{
		{
			name:    "valid API key",
			header:  "ApiKey my-secret-key",
			wantKey: "my-secret-key",
		},
		{
			name:      "missing authorization header",
			header:    "",
			wantError: ErrNoAuthHeaderIncluded,
		},
		{
			name:      "wrong auth scheme",
			header:    "Bearer my-secret-key",
			wantError: errors.New("malformed authorization header"),
		},
		{
			name:      "missing API key",
			header:    "ApiKey",
			wantError: errors.New("malformed authorization header"),
		},
		{
			name:      "empty auth scheme",
			header:    " my-secret-key",
			wantError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			gotKey, err := GetAPIKey(headers)

			if tt.wantError != nil {
				if err == nil {
					t.Fatalf("expected error %q, got nil", tt.wantError)
				}
				if err.Error() != tt.wantError.Error() {
					t.Fatalf("expected error %q, got %q", tt.wantError, err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if gotKey != tt.wantKey {
				t.Errorf("expected key %q, got %q", tt.wantKey, gotKey)
			}
		})
	}
}
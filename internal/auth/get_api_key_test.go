
package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		authHeader    string
		expectedKey   string
		expectedError error
	}{
		{
			name:          "missing authorization header",
			authHeader:    "",
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "malformed authorization header",
			authHeader:    "Bearer token123",
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "authorization header without API key",
			authHeader:    "ApiKey",
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "valid authorization header",
			authHeader:    "ApiKey abc123",
			expectedKey:   "abc123",
			expectedError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}

			if tt.authHeader != "" {
				headers.Set("Authorization", tt.authHeader)
			}

			got, err := GetAPIKey(headers)

			if tt.expectedError != nil {
				if err == nil || err.Error() != tt.expectedError.Error() {
					t.Fatalf("expected error %q, got %v", tt.expectedError, err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if got != tt.expectedKey {
				t.Errorf("expected API key %q, got %q", tt.expectedKey, got)
			}
		})
	}
}


package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct { // anonymous struct slice
		name          string
		authHeader    string // input
		expectedKey   string // expected output
		expectedError error  // expected error (nil = no error)
	}{
		{
			name:          "no header",
			authHeader:    "",
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "wrong prefix",
			authHeader:    "Bearer sometoken",
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "missing key after prefix",
			authHeader:    "ApiKey",
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "valid header",
			authHeader:    "ApiKey my-secret-key",
			expectedKey:   "my-secret-key",
			expectedError: nil,
		},
	}

	for _, tt := range tests { // tt = "table test", conventional name
		t.Run(tt.name, func(t *testing.T) { // t.Run creates a named sub-test
			headers := http.Header{}
			if tt.authHeader != "" {
				headers.Set("Authorization", tt.authHeader)
			}

			got, err := GetAPIKey(headers)

			// Check error
			if tt.expectedError != nil {
				if err == nil {
					t.Fatalf("expected error '%v', got nil", tt.expectedError)
				}
				if err.Error() != tt.expectedError.Error() {
					t.Errorf("expected error '%v', got '%v'", tt.expectedError, err)
				}
			} else if err != nil {
				t.Fatalf("expected no error, got %v", err)
			}

			// Check returned key
			if got != tt.expectedKey {
				t.Errorf("expected key '%s', got '%s'", tt.expectedKey, got)
			}
		})
	}
}

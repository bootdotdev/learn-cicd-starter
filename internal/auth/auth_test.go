package auth_test

import (
	"errors"
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       map[string]string
		expectedKey   string
		expectedError error
	}{
		{
			name:          "valid API key",
			headers:       map[string]string{"Authorization": "ApiKey valid-api-key-123"},
			expectedKey:   "valid-api-key-123",
			expectedError: nil,
		},
		{
			name:          "valid API key with special characters",
			headers:       map[string]string{"Authorization": "ApiKey abc123-def456_ghi789"},
			expectedKey:   "abc123-def456_ghi789",
			expectedError: nil,
		},
		{
			name:          "missing authorization header",
			headers:       map[string]string{},
			expectedKey:   "",
			expectedError: auth.ErrNoAuthHeaderIncluded,
		},
		{
			name:          "empty authorization header",
			headers:       map[string]string{"Authorization": ""},
			expectedKey:   "",
			expectedError: auth.ErrNoAuthHeaderIncluded,
		},
		{
			name:          "malformed authorization header - no space",
			headers:       map[string]string{"Authorization": "ApiKey"},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "malformed authorization header - wrong prefix",
			headers:       map[string]string{"Authorization": "Bearer token123"},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "malformed authorization header - lowercase apikey",
			headers:       map[string]string{"Authorization": "apikey token123"},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "malformed authorization header - only space",
			headers:       map[string]string{"Authorization": " "},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create HTTP headers from the test case
			headers := make(http.Header)
			for key, value := range tt.headers {
				headers.Set(key, value)
			}

			// Call the function
			key, err := auth.GetAPIKey(headers)

			// Check the returned key
			if key != tt.expectedKey {
				t.Errorf("GetAPIKey() key = %v, want %v", key, tt.expectedKey)
			}

			// Check the returned error
			if tt.expectedError == nil {
				if err != nil {
					t.Errorf("GetAPIKey() error = %v, want nil", err)
				}
			} else {
				if err == nil {
					t.Errorf("GetAPIKey() error = nil, want %v", tt.expectedError)
				} else if err.Error() != tt.expectedError.Error() {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.expectedError)
				}
			}
		})
	}
}

func TestGetAPIKey_EdgeCases(t *testing.T) {
	t.Run("case insensitive header name", func(t *testing.T) {
		headers := make(http.Header)
		headers.Set("authorization", "ApiKey test-key") // lowercase header name

		key, err := auth.GetAPIKey(headers)

		if err != nil {
			t.Errorf("GetAPIKey() error = %v, want nil", err)
		}
		if key != "test-key" {
			t.Errorf("GetAPIKey() key = %v, want %v", key, "test-key")
		}
	})

	t.Run("multiple authorization headers", func(t *testing.T) {
		headers := make(http.Header)
		headers.Add("Authorization", "Bearer token1")
		headers.Add("Authorization", "ApiKey test-key")

		key, err := auth.GetAPIKey(headers)

		// Should get the first one (Bearer), which should be malformed
		if err == nil {
			t.Errorf("GetAPIKey() error = nil, want malformed authorization header error")
		}
		if key != "" {
			t.Errorf("GetAPIKey() key = %v, want empty string", key)
		}
	})
}

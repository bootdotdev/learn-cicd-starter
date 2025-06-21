package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		authHeader  string
		wantKey     string
		wantErr     error
		description string
	}{
		{
			name:        "valid API key",
			authHeader:  "ApiKey test-api-key-123",
			wantKey:     "test-api-key-123",
			wantErr:     nil,
			description: "should extract API key from valid Authorization header",
		},
		{
			name:        "API key with spaces",
			authHeader:  "ApiKey test api key with spaces",
			wantKey:     "test",
			wantErr:     nil,
			description: "should extract only the first part after ApiKey when key contains spaces",
		},
		{
			name:        "API key with special characters",
			authHeader:  "ApiKey test-api-key-123!@#$%^&*()",
			wantKey:     "test-api-key-123!@#$%^&*()",
			wantErr:     nil,
			description: "should extract API key with special characters",
		},
		{
			name:        "empty authorization header",
			authHeader:  "",
			wantKey:     "",
			wantErr:     ErrNoAuthHeaderIncluded,
			description: "should return error when no Authorization header is present",
		},
		{
			name:        "missing API key value",
			authHeader:  "ApiKey",
			wantKey:     "",
			wantErr:     errors.New("malformed authorization header"),
			description: "should return error when API key value is missing",
		},
		{
			name:        "wrong prefix",
			authHeader:  "Bearer test-token",
			wantKey:     "",
			wantErr:     errors.New("malformed authorization header"),
			description: "should return error when Authorization header doesn't start with 'ApiKey'",
		},
		{
			name:        "case sensitive prefix",
			authHeader:  "apikey test-api-key",
			wantKey:     "",
			wantErr:     errors.New("malformed authorization header"),
			description: "should return error when 'ApiKey' prefix is not exact case match",
		},
		{
			name:        "multiple spaces before key",
			authHeader:  "ApiKey   test-api-key",
			wantKey:     "",
			wantErr:     nil,
			description: "should return empty string when there are multiple spaces after ApiKey",
		},
		{
			name:        "empty key value",
			authHeader:  "ApiKey ",
			wantKey:     "",
			wantErr:     nil,
			description: "should return empty string for empty API key value",
		},
		{
			name:        "API key with multiple parts",
			authHeader:  "ApiKey part1 part2 part3",
			wantKey:     "part1",
			wantErr:     nil,
			description: "should extract only the first part when API key has multiple space-separated parts",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create headers with the test authorization header
			headers := http.Header{}
			if tt.authHeader != "" {
				headers.Set("Authorization", tt.authHeader)
			}

			// Call the function
			gotKey, gotErr := GetAPIKey(headers)

			// Check the API key
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() key = %v, want %v", gotKey, tt.wantKey)
			}

			// Check the error
			if tt.wantErr == nil {
				if gotErr != nil {
					t.Errorf("GetAPIKey() error = %v, want nil", gotErr)
				}
			} else {
				if gotErr == nil {
					t.Errorf("GetAPIKey() error = nil, want %v", tt.wantErr)
				} else if gotErr.Error() != tt.wantErr.Error() {
					t.Errorf("GetAPIKey() error = %v, want %v", gotErr, tt.wantErr)
				}
			}
		})
	}
}

func TestGetAPIKey_Integration(t *testing.T) {
	// Test with a real HTTP request
	req, err := http.NewRequest("GET", "/test", nil)
	if err != nil {
		t.Fatalf("Failed to create request: %v", err)
	}

	// Test with no Authorization header
	_, err = GetAPIKey(req.Header)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}

	// Test with valid Authorization header
	req.Header.Set("Authorization", "ApiKey test-integration-key")
	key, err := GetAPIKey(req.Header)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if key != "test-integration-key" {
		t.Errorf("Expected 'test-integration-key', got '%s'", key)
	}
}

func TestErrNoAuthHeaderIncluded(t *testing.T) {
	// Test that the error message is correct
	if ErrNoAuthHeaderIncluded.Error() != "no authorization header included" {
		t.Errorf("Expected error message 'no authorization header included', got '%s'", ErrNoAuthHeaderIncluded.Error())
	}
}

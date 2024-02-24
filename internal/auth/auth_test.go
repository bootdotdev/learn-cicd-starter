package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		authHeader     string
		expectedKey    string
		expectingError bool
	}{
		{
			name:           "valid authorization header",
			authHeader:     "ApiKey validKey123",
			expectedKey:    "validKey123",
			expectingError: false,
		},
		{
			name:           "no authorization header",
			authHeader:     "",
			expectedKey:    "",
			expectingError: true,
		},
		{
			name:           "malformed authorization header",
			authHeader:     "Bearer token",
			expectedKey:    "",
			expectingError: true,
		},
		{
			name:           "incorrect prefix",
			authHeader:     "Token someKey",
			expectedKey:    "",
			expectingError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			request, _ := http.NewRequest("GET", "/", nil)
			if tt.authHeader != "" {
				request.Header.Add("Authorization", tt.authHeader)
			}

			key, err := GetAPIKey(request.Header)
			if (err != nil) != tt.expectingError {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.expectingError)
			}
			if key != tt.expectedKey {
				t.Errorf("GetAPIKey() = %v, want %v", key, tt.expectedKey)
			}
		})
	}
}

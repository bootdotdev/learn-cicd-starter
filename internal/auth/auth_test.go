package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "Missing Authorization Header",
			headers:     http.Header{},
			expectedKey: "",
			expectError: true,
			errorMsg:    "no authorization header included",
		},
		{
			name: "Malformed Authorization Header - Missing ApiKey",
			headers: http.Header{
				"Authorization": {"Bearer token"},
			},
			expectedKey: "",
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name: "Malformed Authorization Header - No Space",
			headers: http.Header{
				"Authorization": {"ApiKey"},
			},
			expectedKey: "",
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name: "Correct Authorization Header",
			headers: http.Header{
				"Authorization": {"ApiKey validapikey123"},
			},
			expectedKey: "validapikey123",
			expectError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if tt.expectError {
				if err == nil || err.Error() != tt.errorMsg {
					t.Errorf("expected error '%s', got '%v'", tt.errorMsg, err)
				}
			} else {
				if err != nil {
					t.Errorf("expected no error, got '%v'", err)
				}
				if apiKey != tt.expectedKey {
					t.Errorf("expected API key '%s', got '%s'", tt.expectedKey, apiKey)
				}
			}
		})
	}
}

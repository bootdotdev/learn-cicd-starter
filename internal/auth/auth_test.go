package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name         string
		headers      map[string]string
		expectedKey  string
		expectError  bool
		errorMessage string
	}{
		{
			name:        "Valid API Key",
			headers:     map[string]string{"Authorization": "ApiKey testkey123"},
			expectedKey: "testkey123",
			expectError: false,
		},
		{
			name:         "No Authorization Header",
			headers:      map[string]string{},
			expectError:  true,
			errorMessage: "no authorization header included",
		},
		{
			name:         "Malformed Authorization Header",
			headers:      map[string]string{"Authorization": "Bearer testkey123"},
			expectError:  true,
			errorMessage: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := make(http.Header)
			for k, v := range tt.headers {
				headers.Set(k, v)
			}

			apiKey, err := GetAPIKey(headers)

			if tt.expectError {
				if err == nil || err.Error() != tt.errorMessage {
					t.Errorf("expected error '%s', got '%v'", tt.errorMessage, err)
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

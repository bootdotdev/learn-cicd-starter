package auth

import (
	"errors"
	"net/http"
	"testing"
)

// TestGetAPIKey - test per la funzione GetAPIKey
func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name:          "No Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization Header - Missing ApiKey",
			headers: http.Header{
				"Authorization": {"Bearer some-token"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Authorization Header - Missing Key",
			headers: http.Header{
				"Authorization": {"ApiKey"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Valid Authorization Header",
			headers: http.Header{
				"Authorization": {"ApiKey valid-api-key"},
			},
			expectedKey:   "valid-api-key",
			expectedError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if apiKey != tt.expectedKey {
				t.Fatalf("expected key %s, got %s", tt.expectedKey, apiKey)
			}
			if err != nil && tt.expectedError == nil {
				t.Fatalf("expected no error, got %v", err)
			} else if err == nil && tt.expectedError != nil {
				t.Fatalf("expected error %v, got no error", tt.expectedError)
			} else if err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error() {
				t.Fatalf("expected error %v, got %v", tt.expectedError, err)
			}
		})
	}
}

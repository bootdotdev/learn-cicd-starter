package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey valid_api_key"},
			},
			expectedKey:   "valid_api_key",
			expectedError: nil,
		},
		{
			name:    "No authorization header",
			headers: http.Header{
				// No headers
			},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed authorization header - missing token",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed authorization header - wrong scheme",
			headers: http.Header{
				"Authorization": []string{"Bearer valid_api_key"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actualKey, actualError := GetAPIKey(tt.headers)

			if actualKey != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, actualKey)
			}

			if (actualError == nil && tt.expectedError != nil) || (actualError != nil && tt.expectedError == nil) || (actualError != nil && actualError.Error() != tt.expectedError.Error()) {
				t.Errorf("expected error %v, got %v", tt.expectedError, actualError)
			}
		})
	}
}

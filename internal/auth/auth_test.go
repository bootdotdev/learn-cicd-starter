package auth

import (
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
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey test-api-key-123"},
			},
			expectedKey:   "test-api-key-123",
			expectedError: nil,
		},
		{
			name:          "No Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Missing ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer test-token"},
			},
			expectedKey:   "",
			expectedError: nil, // We'll just check for error presence since the error message is hardcoded in errors.New
		},
		{
			name: "Malformed Header - Missing actual key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: nil,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			if key != tc.expectedKey {
				t.Errorf("expected key: %v, got: %v", tc.expectedKey, key)
			}

			if tc.expectedError != nil {
				if err != tc.expectedError {
					t.Errorf("expected error: %v, got: %v", tc.expectedError, err)
				}
			} else if tc.name != "Valid API Key" {
				// For the malformed cases we just expect some error
				if err == nil {
					t.Errorf("expected an error, got nil")
				}
			} else {
				if err != nil {
					t.Errorf("did not expect error, got: %v", err)
				}
			}
		})
	}
}

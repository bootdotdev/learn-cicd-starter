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
		expectedError string
	}{
		{
			name: "Success: Valid ApiKey",
			headers: http.Header{
				"Authorization": []string{"ApiKey secret-token-123"},
			},
			expectedKey:   "secret-token-123",
			expectedError: "",
		},
		{
			name:          "Error: No Auth Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "Error: Malformed (Wrong Prefix)",
			headers: http.Header{
				"Authorization": []string{"Bearer some-token"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "Error: Malformed (Missing Key)",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if err != nil {
				if tt.expectedError == "" {
					t.Fatalf("unexpected error: %v", err)
				}
				if err.Error() != tt.expectedError {
					t.Errorf("expected error %v, got %v", tt.expectedError, err)
				}
			} else if tt.expectedError != "" {
				t.Errorf("expected error %v, but got none", tt.expectedError)
			}

			if key != tt.expectedKey {
				t.Errorf("expected key %v, got %v", tt.expectedKey, key)
			}
		})
	}
}

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
			name:          "Valid API Key - Standard Case",
			headers:       http.Header{"Authorization": []string{"ApiKey my_secret_api_key"}},
			expectedKey:   "my_secret_api_key",
			expectedError: nil,
		},
		{
			name:          "Missing Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Empty Authorization Header",
			headers:       http.Header{"Authorization": []string{""}},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed Header - Missing ApiKey Prefix",
			headers:       http.Header{"Authorization": []string{"Bearer some_token"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"), // Compare error strings or use a custom error type if possible
		},
		{
			name:          "Malformed Header - Missing API Key Value",
			headers:       http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Case Sensitivity of ApiKey Prefix (Incorrect Case)",
			headers:       http.Header{"Authorization": []string{"apikey my_key"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Empty API Key Value (Potentially Valid/Invalid based on requirements)",
			headers:       http.Header{"Authorization": []string{"ApiKey "}},
			expectedKey:   "",
			expectedError: nil,
		},
		{
			name:          "API Key with Special Characters",
			headers:       http.Header{"Authorization": []string{"ApiKey my_$ecret-key@123!"}},
			expectedKey:   "my_$ecret-key@123!",
			expectedError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}

			// For error comparison, check if both are nil or if their messages match.
			// If you use custom error types or sentinel errors, direct comparison is better.
			if tt.expectedError == nil && err != nil {
				t.Errorf("expected no error, got %v", err)
			} else if tt.expectedError != nil && err == nil {
				t.Errorf("expected error %v, got nil", tt.expectedError)
			} else if tt.expectedError != nil && err != nil && tt.expectedError.Error() != err.Error() {
				t.Errorf("expected error message %q, got %q", tt.expectedError.Error(), err.Error())
			}
		})
	}
}

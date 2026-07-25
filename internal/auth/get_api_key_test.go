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
			name:          "Valid header",
			headers:       http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			expectedKey:   "my-secret-key",
			expectedError: nil,
		},
		{
			name:          "Missing Authorization header",
			headers:       http.Header{},
			expectedKey:   "my-secret-key",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Empty Authorization header",
			headers:       http.Header{"Authorization": []string{""}},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed Authorization header - no space separator",
			headers:       http.Header{"Authorization": []string{"ApiKey-my-secret-key"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Malformed Authorization header - no ApiKey keyword",
			headers:       http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Malformed Authorization header - no key provided",
			headers:       http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("expected key: %v, got: %v", tt.expectedKey, key)
			}

			if (err != nil && tt.expectedError == nil) || (err == nil && tt.expectedError != nil) || (err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error()) {
				t.Errorf("expected error: %v, got: %v", tt.expectedError, err)
			}
		})
	}
}

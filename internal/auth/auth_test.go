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
			name:          "Valid API Key",
			headers:       http.Header{"Authorization": []string{"ApiKey valid-api-key"}},
			expectedKey:   "valid-api-key",
			expectedError: nil,
		},
		{
			name:          "No Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed Authorization Header",
			headers:       http.Header{"Authorization": []string{"invalid-header"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Wrong Prefix in Authorization Header",
			headers:       http.Header{"Authorization": []string{"Bearer token"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)
			if key != test.expectedKey {
				t.Errorf("expected key %q, got %q", test.expectedKey, key)
			}
			if (err != nil && test.expectedError == nil) || (err == nil && test.expectedError != nil) || (err != nil && err.Error() != test.expectedError.Error()) {
				t.Errorf("expected error %v, got %v", test.expectedError, err)
			}
		})
	}
}

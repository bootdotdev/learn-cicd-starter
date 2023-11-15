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
			name:          "Valid Authorization Header",
			headers:       map[string][]string{"Authorization": {"ApiKey your-api-key"}},
			expectedKey:   "your-api-key",
			expectedError: nil,
		},
		{
			name:          "Empty Authorization Header",
			headers:       map[string][]string{"Authorization": {""}},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed Authorization Header",
			headers:       map[string][]string{"Authorization": {"Bearer your-token"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "No Authorization Header",
			headers:       map[string][]string{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)

			if key != test.expectedKey {
				t.Errorf("Expected key %s, but got %s", test.expectedKey, key)
			}

			if err != nil && test.expectedError == nil {
				t.Errorf("Expected no error, but got %v", err)
			}

			if err == nil && test.expectedError != nil {
				t.Errorf("Expected error %v, but got none", test.expectedError)
			}

			if err != nil && test.expectedError != nil && err.Error() != test.expectedError.Error() {
				t.Errorf("Expected error %v, but got %v", test.expectedError, err)
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		authHeader    http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name:          "Valid header",
			authHeader:    http.Header{"Authorization": []string{"ApiKey test-key"}},
			expectedKey:   "test-key",
			expectedError: nil,
		},
		{
			name:          "Missing header",
			authHeader:    http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed header",
			authHeader:    http.Header{"Authorization": []string{"Bearer token"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.authHeader)
			if (err != nil && test.expectedError == nil) || (err == nil && test.expectedError != nil) || (err != nil && test.expectedError != nil && err.Error() != test.expectedError.Error()) {
				t.Errorf("Expected: '%v' but got: '%v'", test.expectedError, err)
			}
			if key != test.expectedKey {
				t.Errorf("Expected: '%v' but got: '%v'", test.expectedKey, key)
			}
		})
	}

}

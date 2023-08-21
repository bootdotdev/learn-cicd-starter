package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test cases
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "ValidAuthorizationHeader",
			headers: http.Header{
				"Authorization": []string{"ApiKey myapikey"},
			},
			expectedKey:   "myapikey",
			expectedError: nil,
		},
		{
			name: "MissingAuthorizationHeader",
			headers: http.Header{
				"X-Some-Other-Header": []string{"somevalue"},
			},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "MalformedAuthorizationHeader",
			headers: http.Header{
				"Authorization": []string{"Bearer token"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)

			if key != test.expectedKey {
				t.Errorf("Expected key: %s, but got: %s", test.expectedKey, key)
			}

			if (err == nil && test.expectedError != nil) || (err != nil && test.expectedError == nil) || (err != nil && test.expectedError != nil && err.Error() != test.expectedError.Error()) {
				t.Errorf("Expected error: %v, but got: %v", test.expectedError, err)
			}
		})
	}
}

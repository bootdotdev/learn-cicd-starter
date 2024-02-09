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
			name:          "No Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"InvalidFormat"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey 12345"},
			},
			expectedKey:   "12345",
			expectedError: "",
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)

			if key != test.expectedKey {
				t.Errorf("expected key %q, got %q", test.expectedKey, key)
			}

			// Check for error consistency
			if err != nil && err.Error() != test.expectedError {
				t.Errorf("expected error %q, got %q", test.expectedError, err.Error())
			} else if err == nil && test.expectedError != "" {
				t.Errorf("expected error %q, but got no error", test.expectedError)
			}
		})
	}
}

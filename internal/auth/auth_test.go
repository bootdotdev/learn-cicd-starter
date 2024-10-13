package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	cases := []struct {
		name          string
		headers       http.Header
		expected      string
		expectedError error
	}{
		{
			name:          "No Authorization header",
			headers:       http.Header{},
			expected:      "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed Authorization header - no ApiKey",
			headers: http.Header{
				"Authorization": {"Linly 12345"},
			},
			expected:      "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "malformed Authorization header - missing key",
			headers: http.Header{
				"Authorization": {"ApiKey"},
			},
			expected:      "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Correct Authorization header",
			headers: http.Header{
				"Authorization": {"ApiKey 12345"},
			},
			expected:      "12345",
			expectedError: nil,
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			actual, err := GetAPIKey(c.headers)

			if c.expectedError != nil && err == nil {
				t.Errorf("expected error %v, but got nil", c.expectedError)
			}
			if c.expectedError == nil && err != nil {
				t.Errorf("did not expect error, but got %v", err)
			}
			if err != nil && err.Error() != c.expectedError.Error() {
				t.Errorf("expected error %v, but got %v", c.expectedError, err)
			}

			if actual != c.expected {
				t.Errorf("expected %v, but got %v", c.expected, actual)
			}
		})
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		expected   string
		expectErr  bool
		errMessage string
	}{
		{
			name: "ValidAuthorizationHeader",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-api-key"},
			},
			expected:   "my-api-key",
			expectErr:  false,
			errMessage: "",
		},
		{
			name:       "NoAuthorizationHeader",
			headers:    http.Header{},
			expected:   "",
			expectErr:  true,
			errMessage: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "MalformedAuthorizationHeader",
			headers: http.Header{
				"Authorization": []string{"InvalidFormat"},
			},
			expected:   "",
			expectErr:  true,
			errMessage: "malformed authorization header",
		},
		{
			name: "EmptyAuthorizationHeaderValue",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expected:   "",
			expectErr:  true,
			errMessage: ErrNoAuthHeaderIncluded.Error(),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			result, err := GetAPIKey(test.headers)
			if test.expectErr {
				if err == nil || err.Error() != test.errMessage {
					t.Errorf("Expected error: %v, got: %v", test.errMessage, err)
				}
			} else if result != test.expected {
				t.Errorf("Expected API key: %s, got: %s", test.expected, result)
			}
		})
	}
}

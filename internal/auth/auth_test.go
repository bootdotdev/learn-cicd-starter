package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test cases
	testCases := []struct {
		name     string
		headers  http.Header
		expected string
		err      error
	}{
		{
			name:     "Valid API key",
			headers:  http.Header{"Authorization": {"ApiKey abc123"}},
			expected: "abc123",
			err:      nil,
		},
		{
			name:     "Missing Authorization header",
			headers:  http.Header{},
			expected: "",
			err:      ErrNoAuthHeaderIncluded,
		},
		{
			name:     "Malformed Authorization header",
			headers:  http.Header{"Authorization": {"Bearer abc123"}},
			expected: "",
			err:      errors.New("malformed authorization header"),
		},
		{
			name:     "Empty API key",
			headers:  http.Header{"Authorization": {"ApiKey "}},
			expected: "",
			err:      nil,
		},
		{
			name:     "Invalid header format",
			headers:  http.Header{"Authorization": {"ApiKey"}},
			expected: "",
			err:      errors.New("malformed authorization header"),
		},
	}

	// Execute test cases
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result, err := GetAPIKey(tc.headers)
			if result != tc.expected {
				t.Errorf("expected '%s', got '%s'", tc.expected, result)
			}
			if (err != nil && tc.err != nil && err.Error() != tc.err.Error()) || (err == nil && tc.err != nil) {
				t.Errorf("expected error '%v', got '%v'", tc.err, err)
			}
		})
	}
}

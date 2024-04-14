package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	cases := []struct {
		input    http.Header
		expected string
		err      error
	}{
		{
			input:    http.Header{"Authorization": []string{"ApiKey 123"}},
			expected: "123",
			err:      nil,
		},
		{
			input:    http.Header{"Authorization": []string{""}},
			expected: "",
			err:      ErrNoAuthHeaderIncluded,
		},
		{
			input:    http.Header{"Authorization": []string{"Bearer 123"}},
			expected: "",
			err:      errors.New("malformed authorization header"),
		},
		{
			input:    http.Header{},
			expected: "",
			err:      ErrNoAuthHeaderIncluded,
		},
	}

	for _, c := range cases {
		actual, err := GetAPIKey(c.input)
		if err != nil {
			if c.err == nil {
				t.Errorf("Unexpected error: %v", err)
			}
			// Here you could add additional checks if needed for custom error types
		} else if c.err != nil {
			t.Errorf("Expected error: %v, but got nil", c.err)
		}

		if actual != c.expected {
			t.Errorf("Expected API key: %s, but got: %s", c.expected, actual)
		}
	}
}

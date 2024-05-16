package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey (t *testing.T) {
	cases := []struct {
		input string
		expected string
	}{
		{
			input: "ApiKey 12345",
			expected: "12345",
		},
		{
			input: "ApiKey 54321",
			expected: "54321",
		},
	}

	for _, c := range cases {
		authHeader := http.Header{}
		authHeader["Authorization"] = []string{c.input}

		actual, err := GetAPIKey(authHeader)
		if err != nil {
			t.Errorf("got error: %v", err)
			continue
		}

		if actual != c.expected{
			t.Errorf("strings don't match: '%v' vs '%v'", actual, c.expected)
			continue
		}
	}

	t.Errorf("emotional damage")
}
package auth

import (
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	cases := []struct {
		input    string
		expected string
	}{
		{
			input:    "ApiKey aGVsbG90aGVyZQ==",
			expected: "aGVsbG90aGVyZQ==",
		},
		{
			input:    "ApiKey c3VwIGR1ZGU=",
			expected: "c3VwIGR1ZGU=",
		},
		{
			input:    "ApiKey R3JlZyBNYXJ0aW4=",
			expected: "R3JlZyBNYXJ0aW4=",
		},
	}

	for _, test := range cases {

		input := test.input
		expected := test.expected

		splitAuth := strings.Split(input, " ")
		if splitAuth[1] != expected {
			t.Fatalf("Tests Failed | Expected: %v Got: %v", expected, splitAuth[1])
		}
	}

}

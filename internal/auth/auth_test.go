package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		headerValue string
		expected    string
		expectError error
	}{
		{
			headerValue: "ApiKey TOKEN_STRING",
			expected:    "TOKEN_STRING",
			expectError: nil,
		},
		{
			headerValue: "",
			expected:    "",
			expectError: errors.New("no authorization header included"),
		},
		{
			headerValue: "Basic TOKEN_STRING",
			expected:    "",
			expectError: errors.New("malformed authorization header"),
		},
		{
			headerValue: "ApiKey",
			expected:    "",
			expectError: errors.New("malformed authorization header"),
		},
	}

	for _, tc := range tests {
		headers := http.Header{}
		headers.Set("Authorization", tc.headerValue)

		token, err := GetAPIKey(headers)
		if err != nil {
			if err.Error() != tc.expectError.Error() {
				t.Fatalf("expected %s, got %s", tc.expectError, err)
			}
			continue
		}

		if token != tc.expected {
			t.Fatalf("expected %s, got %s", tc.expected, token)
		}
	}
}

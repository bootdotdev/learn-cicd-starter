package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testCases := []struct {
		name        string
		authHeader  string
		expected    string
		expectError bool
	}{
		{
			name:        "Valid Token",
			authHeader:  "ApiKey Jojo",
			expected:    "Jojo",
			expectError: false,
		},
		{
			name:        "Bearer instead of ApiKey",
			authHeader:  "Bearer L",
			expected:    "Kira",
			expectError: true,
		},
		{
			name:        "Empty Header",
			authHeader:  "",
			expected:    "",
			expectError: true,
		},
		{
			name:        "No Token",
			authHeader:  "ApiKey ",
			expected:    "",
			expectError: false,
		},
	}
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			headers := make(http.Header)
			headers.Add("Authorization", tc.authHeader)
			apiKey, err := GetAPIKey(headers)
			if tc.expectError && err == nil {
				t.Fatalf("expected error but got none")
			}
			if !tc.expectError && err != nil {
				t.Fatalf("expected no error but got: %v", err)
			}
			if err == nil && apiKey != tc.expected {
				t.Fatalf("expected API key %q, got %q", tc.expected, apiKey)
			}
		})
	}
}

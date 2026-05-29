package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Table-driven test setup
	tests := []struct {
		name         string
		headers      http.Header
		expectedKey  string
		expectingErr bool
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-super-secret-key"},
			},
			expectedKey:  "my-super-secret-key",
			expectingErr: false,
		},
		{
			name:         "Missing Authorization Header",
			headers:      http.Header{},
			expectedKey:  "",
			expectingErr: true,
		},
		{
			name: "Malformed Authorization Header (Wrong Prefix)",
			headers: http.Header{
				"Authorization": []string{"Bearer my-super-secret-key"},
			},
			expectedKey:  "",
			expectingErr: true,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			// Check if we got an error when we weren't expecting one
			if err != nil && !tc.expectingErr {
				t.Fatalf("Test '%s' failed: expected no error, got %v", tc.name, err)
			}

			// Check if we didn't get an error when we were expecting one
			if err == nil && tc.expectingErr {
				t.Fatalf("Test '%s' failed: expected an error, got none", tc.name)
			}

			// Check if the extracted key matches our expectation
			if key != tc.expectedKey {
				t.Fatalf("Test '%s' failed: expected key '%s', got '%s'", tc.name, tc.expectedKey, key)
			}
		})
	}
}

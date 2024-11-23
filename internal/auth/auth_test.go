package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Define test cases
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectedErr error
	}{
		{
			name:        "No Authorization Header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "Malformed Header - Missing ApiKey",
			headers:     http.Header{"Authorization": []string{"Bearer abc123"}},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "Malformed Header - Single Word",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "Valid Header",
			headers:     http.Header{"Authorization": []string{"ApiKey abc123"}},
			expectedKey: "abc123",
			expectedErr: nil,
		},
	}

	// Run each test case
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			// Call the function
			apiKey, err := GetAPIKey(tc.headers)

			// Compare the result
			if apiKey != tc.expectedKey {
				t.Errorf("expected key: %s, got: %s", tc.expectedKey, apiKey)
			}
			if (err == nil && tc.expectedErr != nil) || (err != nil && tc.expectedErr == nil) || (err != nil && err.Error() != tc.expectedErr.Error()) {
				t.Errorf("expected error: %v, got: %v", tc.expectedErr, err)
			}
		})
	}
}

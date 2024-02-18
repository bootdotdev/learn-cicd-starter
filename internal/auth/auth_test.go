package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test cases
	testCases := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectedErr error
	}{
		{
			name:        "Valid Authorization Header",
			headers:     http.Header{"Authorization": []string{"ApiKey my-api-key"}},
			expectedKey: "my-api-key",
			expectedErr: nil,
		},
		{
			name:        "No Authorization Header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "Malformed Authorization Header",
			headers:     http.Header{"Authorization": []string{"InvalidKey"}},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		// Add more test cases as needed
	}

	// Iterate over test cases
	for _, tc := range testCases {
		// Run the test case
		t.Run(tc.name, func(t *testing.T) {
			// Call the function to test
			key, err := GetAPIKey(tc.headers)

			// Check if the result matches the expected value
			if key != tc.expectedKey {
				t.Errorf("GetAPIKey() key = %s; expected %s", key, tc.expectedKey)
			}

			if err != nil && tc.expectedErr == nil {
				t.Errorf("GetAPIKey() unexpected error: %v", err)
			} else if err == nil && tc.expectedErr != nil {
				t.Errorf("GetAPIKey() expected error: %v", tc.expectedErr)
			} else if err != nil && tc.expectedErr != nil && err.Error() != tc.expectedErr.Error() {
				t.Errorf("GetAPIKey() error = %v; expected %v", err, tc.expectedErr)
			}
		})
	}
}

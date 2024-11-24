package auth

import (
	"errors"
	"net/http"
	"testing"
)
makeing test to fail
func TestGetAPIKey(t *testing.T) {
	// Prepare headers
	header0 := make(http.Header)
	header := make(http.Header)
	header2 := make(http.Header)

	key := "ABC-KSJW-32KJF21LJ9-SKJ28-SANDWICH"
	keyString := []string{"ApiKey " + key}
	keyEmpty := []string{"Bear not apiKey "}

	header["Authorization"] = keyEmpty
	header2["Authorization"] = keyString

	// Define test cases
	tests := []struct {
		name           string
		header         http.Header
		expectedAPIKey string
		expectedError  error
	}{
		{
			name:          "No Authorization Header",
			header:        header0, // Match field name
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed Authorization Header - Missing ApiKey",
			header:        header, // Match field name
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:           "Valid Authorization Header",
			header:         header2, // Match field name
			expectedAPIKey: key,
			expectedError:  nil,
		},
	}

	// Run tests
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tc.header)

			// Check error
			if tc.expectedError != nil {
				if err == nil || err.Error() != tc.expectedError.Error() {
					t.Errorf("expected error: %v, got: %v", tc.expectedError, err)
				}
			} else if err != nil {
				t.Errorf("did not expect an error, but got: %v", err)
			}

			// Check API key
			if apiKey != tc.expectedAPIKey {
				t.Errorf("expected API Key: %s, got: %s", tc.expectedAPIKey, apiKey)
			}
		})
	}
}

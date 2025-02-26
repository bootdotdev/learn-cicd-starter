package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testCases := []struct {
		name           string
		headers        http.Header
		expectedAPIKey string
		expectedError  error
	}{
		{
			name:           "Valid API Key",
			headers:        http.Header{"Authorization": {"ApiKey valid-api-key"}},
			expectedAPIKey: "valid-api-key",
			expectedError:  nil,
		},
		{
			name:           "No Authorization Header",
			headers:        http.Header{},
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tc.headers)

			if tc.expectedError != nil && err == nil {
				t.Errorf("Test Case: %s - Expected error, but got none", tc.name)
				return // Stop if error was expected but not received
			}

			if apiKey != tc.expectedAPIKey {
				t.Errorf("Test Case: %s - API Key - Expected '%s', got '%s'", tc.name, tc.expectedAPIKey, apiKey)
			}
		})
	}
}

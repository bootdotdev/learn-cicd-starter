package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testCases := []struct {
		name           string
		headers        http.Header
		expectedKey    string
		expectedErrMsg string
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			expectedKey: "abc123",
		},
		{
			name:           "No Authorization Header",
			headers:        http.Header{},
			expectedErrMsg: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"InvalidKey abc123"},
			},
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "Missing API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedErrMsg: "malformed authorization header",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tc.headers)

			if tc.expectedErrMsg != "" {
				if err == nil {
					t.Errorf("Expected error message: %s, but got nil", tc.expectedErrMsg)
				} else if err.Error() != tc.expectedErrMsg {
					t.Errorf("Expected error message: %s, but got: %s", tc.expectedErrMsg, err.Error())
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %s", err.Error())
				}
				if apiKey != tc.expectedKey {
					t.Errorf("Expected API key: %s, but got: %s", tc.expectedKey, apiKey)
				}
			}
		})
	}
}

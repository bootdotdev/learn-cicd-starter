package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testCases := map[string]struct {
		headers        http.Header
		expectedKey    string
		expectedErrMsg string
	}{
		"Valid API Key": {
			headers: http.Header{
				"Authorization": []string{"ApiKey foo-bar"},
			},
			expectedKey: "foo-bar",
		},
		"Missing Authorization Header": {
			headers:        http.Header{},
			expectedErrMsg: ErrNoAuthHeaderIncluded.Error(),
		},
		"Bearer Authorization Header": {
			headers: http.Header{
				"Authorization": []string{"Bearer foo-bar"},
			},
			expectedErrMsg: "malformed authorization header",
		},
		"Incomplete Header Value": {
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedErrMsg: "malformed authorization header",
		},
	}

	for name, tc := range testCases {
		t.Run(name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tc.headers)

			if tc.expectedErrMsg != "" {
				if err == nil {
					t.Errorf("Expected error message: %s, but no error found", tc.expectedErrMsg)
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

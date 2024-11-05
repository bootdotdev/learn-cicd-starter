package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		name     string
		headers  http.Header
		apiKey   string
		errorMsg string
	}{
		{
			name:     "extract ApiKey from Authorization header",
			headers:  map[string][]string{"Authorization": {"ApiKey 123"}},
			apiKey:   "123",
			errorMsg: "",
		},
		{
			name:     "fail when Authorization header is not found",
			headers:  map[string][]string{},
			apiKey:   "",
			errorMsg: "no authorization header included",
		},
		{
			name:     "fail when Authorization header has no value",
			headers:  map[string][]string{"Authorization": {}},
			apiKey:   "",
			errorMsg: "no authorization header included",
		},
		{
			name:     "fail when Authorization header has wrong auth scheme",
			headers:  map[string][]string{"Authorization": {"Bearer 123"}},
			apiKey:   "",
			errorMsg: "malformed authorization header",
		},
		{
			name:     "fail when Authorization header is malformed",
			headers:  map[string][]string{"Authorization": {"ApiKey123"}},
			apiKey:   "",
			errorMsg: "malformed authorization header",
		},
	}

	for i, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			actual, err := GetAPIKey(tc.headers)
			if err != nil && (tc.errorMsg == "" || !strings.Contains(err.Error(), tc.errorMsg)) {
				t.Errorf("Test %v - '%s' FAIL: unexpected error: %v", i, tc.name, err)
				return
			} else if tc.errorMsg != "" && err == nil {
				t.Errorf("Test %v - '%s' FAIL: expected error: %v, but got none.", i, tc.name, err)
				return
			}

			if actual != tc.apiKey {
				t.Errorf("Test %v - '%s' FAIL: expected ApiKey: %v, actual: %v", i, tc.name, tc.apiKey, actual)
			}
		})
	}
}

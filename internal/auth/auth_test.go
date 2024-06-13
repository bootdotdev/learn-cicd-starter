package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		name         string
		headers      http.Header
		wanted_key   string
		wanted_error error
	}{
		{name: "Invalid API Key",
			headers:    http.Header{"Authorization": []string{"ApiKey my-api-key"}},
			wanted_key: "my-api-key",
		},
		{
			name:         "No Authorization Header Included",
			headers:      http.Header{},
			wanted_error: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			if err != tc.wanted_error {
				t.Errorf("Expected error: %v, got: %v", tc.wanted_error, err)
			}

			if key != tc.wanted_key {
				t.Errorf("Expected key: %s, got: %s", tc.wanted_key, key)
			}
		})
	}
}

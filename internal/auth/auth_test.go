package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedAPIKey string
		expectedErr    error
	}{
		{
			name:        "Missing Authorization header",
			headers:     http.Header{},
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization header with no ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer some-token"},
			},
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Authorization header with missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "Valid Authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey valid-api-key"},
			},
			expectedAPIKey: "valid-api-key",
			expectedErr:    nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)

			if apiKey != tt.expectedAPIKey {
				t.Errorf("expected API key: %v, got: %v", tt.expectedAPIKey, apiKey)
			}

			if (err != nil && tt.expectedErr == nil) || (err == nil && tt.expectedErr != nil) || (err != nil && err.Error() != tt.expectedErr.Error()) {
				t.Errorf("expected error: %v, got: %v", tt.expectedErr, err)
			}
		})
	}
}

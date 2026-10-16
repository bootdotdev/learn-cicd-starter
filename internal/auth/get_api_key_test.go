package auth

import (
	"net/http"
	"testing"

	"errors"
	"github.com/stretchr/testify/require"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey valid_api_key"},
			},
			expectedKey:   "valid_api_key",
			expectedError: nil,
		},
		{
			name: "No Authorization Header",
			headers: http.Header{
				"Content-Type": []string{"application/json"},
			},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"Bearer some_token"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			require.Equal(t, tt.expectedKey, apiKey)
			require.Equal(t, tt.expectedError, err)
		})
	}
}

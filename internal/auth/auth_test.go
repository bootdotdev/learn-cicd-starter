package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headerKey   string
		headerValue string
		expectedKey string
		expectedErr error
	}{
		{
			name:        "Valid API Key in Header",
			headerKey:   "Authorization",
			headerValue: "ApiKey secret123",
			expectedKey: "secret123",
			expectedErr: nil,
		},
		{
			name:        "Missing Authorization Header",
			headerKey:   "",
			headerValue: "",
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "Malformed Authorization Header - Missing ApiKey Prefix",
			headerKey:   "Authorization",
			headerValue: "Bearer secret123",
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "Malformed Authorization Header - No Key Provided",
			headerKey:   "Authorization",
			headerValue: "ApiKey",
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "Malformed Authorization Header - Extra Spaces",
			headerKey:   "Authorization",
			headerValue: "ApiKey   secret123",
			expectedKey: "secret123", // Acceptable if extra spaces are ignored
			expectedErr: nil,         // No error expected if spaces are ignored
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			headers := make(http.Header)
			if tc.headerKey != "" {
				headers.Set(tc.headerKey, tc.headerValue)
			}

			apiKey, err := GetAPIKey(headers)

			if apiKey != tc.expectedKey {
				t.Errorf("expected API key %q, got %q", tc.expectedKey, apiKey)
			}

			if err != nil && tc.expectedErr == nil {
				t.Errorf("unexpected error: %v", err)
			} else if err == nil && tc.expectedErr != nil {
				t.Errorf("expected error %v, got nil", tc.expectedErr)
			} else if err != nil && tc.expectedErr != nil && err.Error() != tc.expectedErr.Error() {
				t.Errorf("expected error %q, got %q", tc.expectedErr.Error(), err.Error())
			}
		})
	}
}

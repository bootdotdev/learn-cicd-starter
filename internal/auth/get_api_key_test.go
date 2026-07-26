package auth

import (
	"errors"
	"net/http"
	"testing"
)


func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name string
		headers http.Header
		expectedKey string
		expectedError error
	} {
		{
			name: "Success - Header valid",
			headers: http.Header {
				"Authorization": []string{"ApiKey secret-token-12345"},
			},
			expectedKey: "secret-token-12345",
			expectedError: nil,
		},
		{
			name: "Fail - Header invalid",
			headers: http.Header { },
			expectedKey: "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Fail - Mising prefix ApiKey",
			headers: http.Header {
				"Authorization": []string{"Bearer secret-token-12345"},
			},
			expectedKey: "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Fail - Header is missing token",
			headers: http.Header {
				"Authorization": []string{"ApiKey"},
			},
			expectedKey: "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Faile - Header empty",
			headers: http.Header {
				"Authorization": []string{""},
			},
			expectedKey: "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.expectedError != nil {
				if err == nil {
					t.Fatalf("Excepted '%v' but actual", tt.expectedError)
				}
				if err.Error() != tt.expectedError.Error() {
					t.Errorf("Error get: '%v', expected: '%v'", err, tt.expectedError)
				}
			} else {
				if err != nil {
					t.Fatalf("Excepeted no errors, but get error: '%v'", err)
				}
			}

			if key != tt.expectedKey {
				t.Errorf("key get: '%s', expected: '%s'", key, tt.expectedKey)
			}

		})
	}
		
}

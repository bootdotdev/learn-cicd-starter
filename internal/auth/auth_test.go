package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name:          "no authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed header",
			headers: http.Header{
				"Authorization": []string{"FoobarHeader"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "valid ApiKey",
			headers: http.Header{
				"Authorization": []string{"ApiKey testing123"},
			},
			expectedKey:   "testing123",
			expectedError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("%v: want %v, got %v", tt.name, tt.expectedKey, key)
			}

			// Check if error occurs which is unexpected, and vice versa.
			if (err != nil) != (tt.expectedError != nil) {
				t.Errorf("GetAPIKey() error = %v, want %v", err, tt.expectedError)
			}

			// Check if the error occurred has the expected message.
			if err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error() {
				t.Errorf("GetAPIKey() error = %v, want %v", err, tt.expectedError)
			}
		})
	}
}

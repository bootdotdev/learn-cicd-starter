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
			name:          "No Authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Authorization header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer token123"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Valid Authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey test123"},
			},
			expectedKey:   "test123",
			expectedError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)
			if err != nil && tt.expectedError == nil {
				t.Errorf("GetAPIKey() unexpected error = %v", err)
				return
			}
			if err == nil && tt.expectedError != nil {
				t.Errorf("GetAPIKey() expected error = %v, got nil", tt.expectedError)
				return
			}
			if err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error() {
				t.Errorf("GetAPIKey() error = %v, expected error = %v", err, tt.expectedError)
				return
			}
			if key != tt.expectedKey {
				t.Errorf("GetAPIKey() key = %v, expected key = %v", key, tt.expectedKey)
			}
		})
	}
}

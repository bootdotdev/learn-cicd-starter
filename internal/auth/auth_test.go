package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		header        http.Header
		expectedKey   string
		expectingErr  bool
		expectedError error
	}{
		{
			name:         "valid header",
			header:       http.Header{"Authorization": []string{"ApiKey abc123"}},
			expectedKey:  "abc123",
			expectingErr: false,
		},
		{
			name:          "no header",
			header:        http.Header{},
			expectedKey:   "",
			expectingErr:  true,
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "malformed header",
			header:        http.Header{"Authorization": []string{"Bearer abc123"}},
			expectedKey:   "",
			expectingErr:  true,
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.header)

			if tt.expectingErr {
				if err == nil {
					t.Errorf("expected error but got nil")
				} else if err.Error() != tt.expectedError.Error() {
					t.Errorf("expected error '%v', got '%v'", tt.expectedError, err)
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
				}
				if key != tt.expectedKey {
					t.Errorf("expected key '%s', got '%s'", tt.expectedKey, key)
				}
			}
		})
	}
}

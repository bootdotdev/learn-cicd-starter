package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeySimplified(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectedErr error
	}{
		{
			name:        "No authorization header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Well-formed authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey validkey123"},
			},
			expectedKey: "validkey123",
			expectedErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("Test '%s' failed: expected key %q, got %q", tt.name, tt.expectedKey, key)
			}

			if tt.expectedErr != nil {
				if err == nil || err.Error() != tt.expectedErr.Error() {
					t.Errorf("Test '%s' failed: expected error %v, got %v", tt.name, tt.expectedErr, err)
				}
			} else if err != nil {
				t.Errorf("Test '%s' failed: expected no error, got %v", tt.name, err)
			}
		})
	}
}

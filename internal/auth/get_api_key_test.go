package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectedErr error
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key-123"},
			},
			expectedKey: "my-secret-key-123",
			expectedErr: nil,
		},
		{
			name:        "No Authorization Header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Empty Authorization Header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Wrong Prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-key-123"},
			},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Header - Missing Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}

			if tt.expectedErr != nil {
				if err == nil {
					t.Errorf("expected error %q, got nil", tt.expectedErr.Error())
				} else if err.Error() != tt.expectedErr.Error() {
					t.Errorf("expected error %q, got %q", tt.expectedErr.Error(), err.Error())
				}
			} else if err != nil {
				t.Errorf("expected no error, got %q", err.Error())
			}
		})
	}
}

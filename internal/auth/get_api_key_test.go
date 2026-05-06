package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		testName    string
		headers     http.Header
		expectedKey string
		expectedErr error
		errText     string
	}{
		{
			testName:    "No Authorization header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			testName: "Empty Authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			testName: "Malformed header - missing API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey: "",
			errText:     "malformed authorization header",
		},
		{
			testName: "Malformed header - wrong scheme",
			headers: http.Header{
				"Authorization": []string{"Bearer 12345"},
			},
			expectedKey: "",
			errText:     "malformed authorization header",
		},
		{
			testName: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey super-secret-key-123"},
			},
			expectedKey: "super-secret-key-123",
			expectedErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.testName, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("expectedKey: %q, got %q", tt.expectedKey, key)
			}

			if tt.expectedErr != nil {
				if !errors.Is(err, tt.expectedErr) {
					t.Errorf("expectedErr %v, got %v", tt.expectedErr, err)
				}
			} else if tt.errText != "" {
				if err == nil || !strings.Contains(err.Error(), tt.errText) {
					t.Errorf("expected error containting %q, got %v", tt.errText, err)
				}
			} else {
				if err != nil {
					t.Errorf("expected no error, got %v", err)
				}
			}
		})
	}
}

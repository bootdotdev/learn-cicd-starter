package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedKey    string
		expectedErr    bool
		expectedErrStr string
	}{
		{
			name:        "Valid ApiKey header",
			headers:     http.Header{"Authorization": []string{"ApiKey my-secret-token-123"}},
			expectedKey: "my-secret-token-123",
			expectedErr: false,
		},
		{
			name:           "Missing Authorization header",
			headers:        http.Header{},
			expectedKey:    "",
			expectedErr:    true,
			expectedErrStr: "no authorization header included",
		},
		{
			name:           "Malformed header - missing token",
			headers:        http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:    "",
			expectedErr:    true,
			expectedErrStr: "malformed authorization header",
		},
		{
			name:           "Malformed header - wrong prefix",
			headers:        http.Header{"Authorization": []string{"Bearer my-token"}},
			expectedKey:    "",
			expectedErr:    true,
			expectedErrStr: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			// Check error expectations
			if (err != nil) != tt.expectedErr {
				t.Fatalf("expected error: %v, got: %v", tt.expectedErr, err)
			}

			// Validate error message if an error is expected
			if tt.expectedErr && err.Error() != tt.expectedErrStr {
				t.Errorf("expected error message %q, got %q", tt.expectedErrStr, err.Error())
			}

			// Check returned API key
			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}
		})
	}
}

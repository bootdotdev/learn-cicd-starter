package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectError   bool
		errorContains string
	}{
		{
			name: "valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			expectedKey: "my-secret-key",
			expectError: false,
		},
		{
			name:          "missing authorization header",
			headers:       http.Header{},
			expectError:   true,
			errorContains: "no authorization header included",
		},
		{
			name: "malformed header - missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectError:   true,
			errorContains: "malformed authorization header",
		},
		{
			name: "malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer token123"},
			},
			expectError:   true,
			errorContains: "malformed authorization header",
		},
		{
			name: "extra spaces but valid format",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key extra"},
			},
			expectedKey: "my-secret-key",
			expectError: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			if tc.expectError {
				if err == nil {
					t.Fatalf("expected error but got nil")
				}
				if tc.errorContains != "" && err.Error() != tc.errorContains {
					t.Fatalf("expected error %q, got %q", tc.errorContains, err.Error())
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if key != tc.expectedKey {
				t.Fatalf("expected key %q, got %q", tc.expectedKey, key)
			}
		})
	}
}

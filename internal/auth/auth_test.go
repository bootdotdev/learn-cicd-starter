package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		authHeader    string
		wantKey       string
		wantErrSubstr string
	}{
		{
			name:          "missing header",
			authHeader:    "",
			wantErrSubstr: "authorization header is missing",
		},
		{
			name:          "wrong prefix",
			authHeader:    "Bearer abc123",
			wantErrSubstr: "must start with 'ApiKey '",
		},
		{
			name:          "empty key after prefix",
			authHeader:    "ApiKey ",
			wantErrSubstr: "API key is missing",
		},
		{
			name:       "Valid key",
			authHeader: "ApiKey my-secret-key",
			wantKey:    "my-secret-key", //correct
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req, _ := http.NewRequest("GET", "/", nil)
			if tc.authHeader != "" {
				req.Header.Set("Authorization", tc.authHeader)
			}

			gotKey, err := GetAPIKey(req)

			if tc.wantErrSubstr != "" {
				if err == nil || !contains(err.Error(), tc.wantErrSubstr) {
					t.Errorf("expected error containing %q, got %v", tc.wantErrSubstr, err)
				}
				return
			}

			if err != nil {
				t.Errorf("unexpected error: %v", err)
			}
			if gotKey != tc.wantKey {
				t.Errorf("expected key %q, got %q", tc.wantKey, gotKey)
			}
		})
	}
}

func contains(s, substr string) bool {
	return len(substr) == 0 || (len(s) >= len(substr) && stringContains(s, substr))
}

func stringContains(s, substr string) bool {
	return len(substr) <= len(s) && (indexOf(s, substr) >= 0)
}

func indexOf(s, substr string) int {
	for i := range s {
		if len(s)-i < len(substr) {
			return -1
		}
		if s[i:i+len(substr)] == substr {
			return i
		}
	}
	return -1
}
// trigger CI

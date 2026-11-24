package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		wantKey   string
		wantError bool
	}{
		{
			name:    "valid header",
			headers: http.Header{"Authorization": []string{"ApiKey abc123"}},
			wantKey: "abc123",
		},
		{
			name:      "no authorization header",
			headers:   http.Header{},
			wantError: true,
		},
		{
			name:      "empty authorization header",
			headers:   http.Header{"Authorization": []string{""}},
			wantError: true,
		},
		{
			name:      "wrong prefix",
			headers:   http.Header{"Authorization": []string{"Bearer abc123"}},
			wantError: true,
		},
		{
			name:      "missing key after prefix",
			headers:   http.Header{"Authorization": []string{"ApiKey"}},
			wantError: true,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			if tc.wantError && err == nil {
				t.Fatalf("expected an error, got none")
			}
			if !tc.wantError && err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.wantKey {
				t.Fatalf("expected key %q, got %q", tc.wantKey, got)
			}
		})
	}
}

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
			name: "success - valid ApiKey header",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			wantKey:   "abc123",
			wantError: false,
		},
		{
			name:      "error - missing Authorization header",
			headers:   http.Header{},
			wantKey:   "",
			wantError: true,
		},
		{
			name: "error - malformed header missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			wantKey:   "",
			wantError: true,
		},
		{
			name: "error - wrong auth type",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			wantKey:   "",
			wantError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.wantError && err == nil {
				t.Fatalf("expected error, got nil")
			}

			if !tt.wantError && err != nil {
				t.Fatalf("did not expect error, got %v", err)
			}

			if key != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, key)
			}
		})
	}
}

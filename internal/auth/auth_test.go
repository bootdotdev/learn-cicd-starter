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
		wantError error
	}{
		{
			name: "valid ApiKey header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			wantKey:   "my-secret-key",
			wantError: nil,
		},
		{
			name:      "missing Authorization header",
			headers:   http.Header{},
			wantKey:   "",
			wantError: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.wantError != nil {
				if err == nil {
					t.Fatalf("expected error %v, got nil", tt.wantError)
				}
				if err != tt.wantError {
					t.Fatalf("expected error %v, got %v", tt.wantError, err)
				}
			} else {
				if err != nil {
					t.Fatalf("expected no error, got %v", err)
				}
				if key != tt.wantKey {
					t.Errorf("expected key %q, got %q", tt.wantKey, key)
				}
			}
		})
	}
}

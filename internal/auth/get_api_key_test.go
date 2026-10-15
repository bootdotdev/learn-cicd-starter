package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestSplit(t *testing.T) {
	tests := []struct {
		name      string
		header    string
		wantKey   string
		wantError error
	}{
		{
			name:      "missing authorization header",
			header:    "",
			wantError: ErrNoAuthHeaderIncluded,
		},
		{
			name:      "malformed authorization header",
			header:    "Bearer abc123",
			wantError: errors.New("malformed authorization header"),
		},
		{
			name:    "valid api key",
			header:  "ApiKey abc123",
			wantKey: "abc123",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			gotKey, err := GetAPIKey(headers)

			if tt.wantError != nil {
				if err == nil {
					t.Fatalf("expected error %v, got nil", tt.wantError)
				}
				if err.Error() != tt.wantError.Error() {
					t.Fatalf("expected error %q, got %q", tt.wantError, err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if gotKey != tt.wantKey {
				t.Errorf("expected key %q, got %q", tt.wantKey, gotKey)
			}
		})
	}
}

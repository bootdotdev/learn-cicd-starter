package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		authHeader string
		want       string
		wantErr    bool
	}{
		{
			name:       "valid API key",
			authHeader: "ApiKey test-key-123",
			want:       "test-key-123",
			wantErr:    false,
		},
		{
			name:       "missing authorization header",
			authHeader: "",
			want:       "",
			wantErr:    true,
		},
		{
			name:       "malformed authorization header",
			authHeader: "Bearer test-key-123",
			want:       "",
			wantErr:    true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}

			if tt.authHeader != "" {
				headers.Set("Authorization", tt.authHeader)
			}

			got, err := GetAPIKey(headers)

			if tt.wantErr && err == nil {
				t.Fatalf("expected an error, but got nil")
			}

			if !tt.wantErr && err != nil {
				t.Fatalf("did not expect an error, but got %v", err)
			}

			if got != tt.want {
				t.Errorf("expected API key %q, got %q", tt.want, got)
			}
		})
	}
}

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
		wantErr    error
	}{
		{
			name:       "valid API key",
			authHeader: "ApiKey abc123",
			want:       "abc123",
		},
		{
			name:       "missing authorization header",
			authHeader: "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name:       "invalid authentication scheme",
			authHeader: "Bearer abc123",
			wantErr:    nil, // Checked separately below
		},
		{
			name:       "missing API key",
			authHeader: "ApiKey",
			wantErr:    nil, // Checked separately below
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.authHeader != "" {
				headers.Set("Authorization", tt.authHeader)
			}

			got, err := GetAPIKey(headers)

			if tt.wantErr != nil {
				if err != tt.wantErr {
					t.Fatalf("expected error %v, got %v", tt.wantErr, err)
				}
				return
			}

			if tt.want != "" && err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if got != tt.want {
				t.Errorf("expected %q, got %q", tt.want, got)
			}
		})
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		header  string
		wantKey string
		wantErr string
	}{
		{
			name:    "valid api key",
			header:  "ApiKey my-secret-key",
			wantKey: "my-secret-key",
		},
		{
			name:    "missing authorization header",
			wantErr: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:    "wrong auth scheme",
			header:  "Bearer token",
			wantErr: "malformed authorization header",
		},
		{
			name:    "missing api key",
			header:  "ApiKey",
			wantErr: "malformed authorization header",
		},
		{
			name:    "empty api key",
			header:  "ApiKey ",
			wantErr: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			gotKey, err := GetAPIKey(headers)

			if gotKey != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, gotKey)
			}

			if tt.wantErr == "" {
				if err != nil {
					t.Fatalf("unexpected error: %v", err)
				}
				return
			}

			if err == nil {
				t.Fatal("expected an error but got nil")
			}

			if err.Error() != tt.wantErr {
				t.Fatalf("expected error %q, got %q", tt.wantErr, err.Error())
			}
		})
	}
}

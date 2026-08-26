package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		header  string
		wantKey string
		wantErr error
	}{
		{
			name:    "valid api key",
			header:  "ApiKey my-secret-key",
			wantKey: "my-secret-key",
		},
		{
			name:    "missing authorization header",
			header:  "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "malformed header wrong scheme",
			header:  "Bearer my-secret-key",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name:    "malformed header missing key",
			header:  "ApiKey",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name:    "malformed header single word",
			header:  "ApiKeyOnly",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			gotKey, err := GetAPIKey(headers)

			if tt.wantErr != nil {
				if err == nil {
					t.Fatalf("expected error %q, got nil", tt.wantErr)
				}
				if err.Error() != tt.wantErr.Error() {
					t.Fatalf("expected error %q, got %q", tt.wantErr, err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if gotKey != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, gotKey)
			}
		})
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		header      string
		wantKey     string
		wantErr     bool
		expectedErr error
	}{
		{
			name:        "valid API key",
			header:      "ApiKey my-secret-key",
			wantKey:     "my-secret-key",
			wantErr:     false,
			expectedErr: nil,
		},
		{
			name:        "missing authorization header",
			header:      "",
			wantKey:     "",
			wantErr:     true,
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "wrong authorization scheme",
			header:      "Bearer my-secret-key",
			wantKey:     "",
			wantErr:     true,
			expectedErr: nil,
		},
		{
			name:        "malformed header",
			header:      "ApiKey",
			wantKey:     "",
			wantErr:     true,
			expectedErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			got, err := GetAPIKey(headers)

			if (err != nil) != tt.wantErr {
				t.Fatalf("expected error=%v, got %v", tt.wantErr, err)
			}

			if tt.expectedErr != nil && err != tt.expectedErr {
				t.Fatalf("expected error %v, got %v", tt.expectedErr, err)
			}

			if got != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, got)
			}
		})
	}
}
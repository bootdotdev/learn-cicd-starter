package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		wantKey   string
		wantErr   bool
		wantErrIs error
	}{
		{
			name:    "valid ApiKey header",
			headers: http.Header{"Authorization": []string{"ApiKey abc123"}},
			wantKey: "abc123",
		},
		{
			name:      "missing Authorization header",
			headers:   http.Header{},
			wantErr:   true,
			wantErrIs: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "wrong auth scheme",
			headers: http.Header{"Authorization": []string{"Bearer abc123"}},
			wantErr: true,
		},
		{
			name:    "scheme without a key",
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if tt.wantErr {
				if err == nil {
					t.Fatalf("expected an error, got nil (key=%q)", got)
				}
				if tt.wantErrIs != nil && !errors.Is(err, tt.wantErrIs) {
					t.Fatalf("expected error %v, got %v", tt.wantErrIs, err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, got)
			}
		})
	}
}

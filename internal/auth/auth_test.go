package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantKey    string
		wantErr    bool
		wantErrMsg string
	}{
		{
			name:    "returns API key when header is valid",
			headers: http.Header{"Authorization": []string{"ApiKey secret-key"}},
			wantKey: "secret-key",
		},
		{
			name:       "returns error when authorization header is missing",
			headers:    http.Header{},
			wantErr:    true,
			wantErrMsg: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:       "returns error when scheme is incorrect",
			headers:    http.Header{"Authorization": []string{"Bearer secret-key"}},
			wantErr:    true,
			wantErrMsg: "malformed authorization header",
		},
		{
			name:       "returns error when header is malformed",
			headers:    http.Header{"Authorization": []string{"ApiKey"}},
			wantErr:    true,
			wantErrMsg: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			if tt.wantErr {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}
				if err.Error() != tt.wantErrMsg {
					t.Fatalf("expected error %q, got %q", tt.wantErrMsg, err.Error())
				}

				if tt.wantErrMsg == ErrNoAuthHeaderIncluded.Error() && !errors.Is(err, ErrNoAuthHeaderIncluded) {
					t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
				}

				return
			}

			if err != nil {
				t.Fatalf("expected nil error, got %v", err)
			}

			if gotKey != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, gotKey)
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKeyReturnsKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey secret-key")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if got != "secret-key" {
		t.Fatalf("expected API key %q, got %q", "secret-key", got)
	}
}

func TestGetAPIKeyErrors(t *testing.T) {
	tests := []struct {
		name    string
		header  string
		wantErr error
	}{
		{
			name:    "missing authorization header",
			header:  "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "malformed authorization header",
			header:  "Bearer secret-key",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			_, err := GetAPIKey(headers)
			if err == nil {
				t.Fatal("expected an error, got nil")
			}

			if err.Error() != tt.wantErr.Error() {
				t.Fatalf("expected error %q, got %q", tt.wantErr.Error(), err.Error())
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		authValue  string
		wantKey    string
		wantErr    error
		wantErrMsg string
	}{
		{
			name:      "missing header",
			authValue: "",
			wantErr:   ErrNoAuthHeaderIncluded,
		},
		{
			name:       "malformed header",
			authValue:  "Bearer abc123",
			wantErrMsg: "malformed authorization header",
		},
		{
			name:      "valid api key",
			authValue: "ApiKey abc123",
			wantKey:   "abc123",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			headers := http.Header{}
			if tc.authValue != "" {
				headers.Set("Authorization", tc.authValue)
			}

			gotKey, err := GetAPIKey(headers)
			if tc.wantErr != nil {
				if !errors.Is(err, tc.wantErr) {
					t.Fatalf("expected error %v, got %v", tc.wantErr, err)
				}
				return
			}
			if tc.wantErrMsg != "" {
				if err == nil || err.Error() != tc.wantErrMsg {
					t.Fatalf("expected error %q, got %v", tc.wantErrMsg, err)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if gotKey != tc.wantKey {
				t.Fatalf("expected key %q, got %q", tc.wantKey, gotKey)
			}
		})
	}
}

/*
// Teste intencionalmente quebrado para demonstrar falha de teste

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Broken(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey abc123")

	gotKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if gotKey != "def456" {
		t.Fatalf("expected key %q, got %q", "def456", gotKey)
	}
}
*/

package auth

import (
	"errors"
	"net/http"
	"testing"
)

const malformedMsg = "malformed authorization header"

func TestGetAPIKey(t *testing.T) {
	t.Parallel()

	type tc struct {
		name          string
		authValue     *string // nil => header absent
		wantKey       string  // expected key on success
		wantErrIsNoAH bool    // expect ErrNoAuthHeaderIncluded
		wantErrMsg    string  // exact error message expected
	}

	tests := []tc{
		{
			name:          "no Authorization header",
			authValue:     nil,
			wantErrIsNoAH: true,
		},
		{
			name:       "wrong scheme (Bearer)",
			authValue:  strPtr("Bearer abc123"),
			wantErrMsg: malformedMsg,
		},
		{
			name:       "missing token after ApiKey (only scheme)",
			authValue:  strPtr("ApiKey"),
			wantErrMsg: malformedMsg,
		},
		{
			name:      "ApiKey with extra spaces returns empty token (current behavior)",
			authValue: strPtr("ApiKey     "),
			wantKey:   "", // current implementation returns splitAuth[1] == ""
		},
		{
			name:      "happy path",
			authValue: strPtr("ApiKey secret-token-xyz"),
			wantKey:   "secret-token-xyz",
		},
		{
			name:      "extra parts beyond token: returns first token (current behavior)",
			authValue: strPtr("ApiKey abc def"),
			wantKey:   "abc",
		},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			h := http.Header{}
			if tt.authValue != nil {
				h.Set("Authorization", *tt.authValue)
			}

			got, err := GetAPIKey(h)

			// expect the special "no auth header" error
			if tt.wantErrIsNoAH {
				if !errors.Is(err, ErrNoAuthHeaderIncluded) {
					t.Fatalf("expected ErrNoAuthHeaderIncluded, got: %v", err)
				}
				return
			}

			// expect a specific error message
			if tt.wantErrMsg != "" {
				if err == nil {
					t.Fatalf("expected error %q, got nil", tt.wantErrMsg)
				}
				if err.Error() != tt.wantErrMsg {
					t.Fatalf("expected error %q, got %q", tt.wantErrMsg, err.Error())
				}
				return
			}

			// expect success (no error) and the key
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, got)
			}
		})
	}
}

func strPtr(s string) *string { return &s }

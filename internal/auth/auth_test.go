package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		authHeader    string
		wantKey       string
		wantErr       error
		wantErrSubstr string
	}{
		"valid ApiKey header": {
			authHeader: "ApiKey abc123",
			wantKey:    "abc123",
		},
		"missing Authorization header": {
			authHeader: "",
			wantKey:    "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		"wrong scheme": {
			authHeader:    "Bearer abc123",
			wantKey:       "",
			wantErrSubstr: "malformed authorization header",
		},
		"missing key after ApiKey": {
			authHeader:    "ApiKey",
			wantKey:       "",
			wantErrSubstr: "malformed authorization header",
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			h := make(http.Header)
			if tc.authHeader != "" {
				h.Set("Authorization", tc.authHeader)
			}

			gotKey, gotErr := GetAPIKey(h)

			if gotKey != tc.wantKey {
				t.Fatalf("expected key %q, got %q", tc.wantKey, gotKey)
			}

			// Exact error match (for sentinel errors)
			if tc.wantErr != nil {
				if gotErr != tc.wantErr {
					t.Fatalf("expected error %v, got %v", tc.wantErr, gotErr)
				}
				return
			}

			// Substring match (for non-sentinel errors like errors.New(...))
			if tc.wantErrSubstr != "" {
				if gotErr == nil {
					t.Fatalf("expected error containing %q, got nil", tc.wantErrSubstr)
				}
				if !strings.Contains(gotErr.Error(), tc.wantErrSubstr) {
					t.Fatalf("expected error containing %q, got %q", tc.wantErrSubstr, gotErr.Error())
				}
				return
			}

			// Expect no error
			if gotErr != nil {
				t.Fatalf("expected no error, got %v", gotErr)
			}
		})
	}
}

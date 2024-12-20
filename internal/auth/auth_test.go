package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers     http.Header
		wantKey     string
		wantErr     bool
		errorString string
	}{
		"valid authorization header": {
			headers: http.Header{"Authorization": []string{"ApiKey " + "validKey"}},
			wantKey: "validKey",
			wantErr: false,
		},
		"missing authorization header": {
			headers:     http.Header{},
			wantErr:     true,
			errorString: "no authorization header included",
		},
		"incorrect scheme": {
			headers:     http.Header{"Authorization": []string{"Bearer " + "validKey"}},
			wantErr:     true,
			errorString: "malformed authorization header",
		},
		"mutliple keys": {
			headers: http.Header{"Authorization": []string{"ApiKey key1 key2"}},
			wantKey: "key1",
			wantErr: false,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tc.headers)
			if (err != nil) != tc.wantErr {
				t.Fatalf("error: %v, wantErr: %v", err, tc.wantErr)
				return
			}
			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected error but got none")
				} else if !strings.Contains(err.Error(), tc.errorString) {
					t.Fatalf("error: %v, expected substring: %v", err, tc.errorString)
				}
				return
			}
			if gotKey != tc.wantKey {
				t.Fatalf("got: %v, want: %v", gotKey, tc.wantKey)
			}
		})
	}
}

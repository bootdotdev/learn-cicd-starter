package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPiKey(t *testing.T) {
	type test struct {
		name    string
		input   http.Header
		want    string
		wanterr string
	}
	tests := []test{
		{name: "valid input", input: http.Header{"Authorization": []string{"ApiKey mysecretapikey123"}}, want: "mysecretapikey123", wanterr: ""},
		{name: "no auth header", input: http.Header{"Accept": []string{"application/json"}}, want: "", wanterr: "no authorization header included"},
		{name: "malformed auth header", input: http.Header{"Authorization": []string{"Bearer token123"}}, want: "", wanterr: "malformed authorization header"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			if tc.wanterr != "" {
				if err == nil {
					t.Fatalf("expected error containing %q, got nil", tc.wanterr)
				}
				if !strings.Contains(err.Error(), tc.wanterr) {
					t.Fatalf("expected error containing %q, got %q", tc.wanterr, err.Error())
				}
			} else if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if got != tc.want {
				t.Errorf("expected value %q, got %q", tc.want, got)
			}
		})
	}
}

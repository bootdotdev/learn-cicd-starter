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
		want    string
		wantErr bool
		errIs   error
	}{
		{name: "valid key", header: "ApiKey abc123", want: "abc123"},
		{name: "missing header", header: "", wantErr: true, errIs: ErrNoAuthHeaderIncluded},
		{name: "wrong scheme", header: "Bearer abc123", wantErr: true},
		{name: "no key value", header: "ApiKey", wantErr: true},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			h := http.Header{}
			if tc.header != "" {
				h.Set("Authorization", tc.header)
			}
			got, err := GetAPIKey(h)
			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}
				if tc.errIs != nil && !errors.Is(err, tc.errIs) {
					t.Fatalf("expected error %v, got %v", tc.errIs, err)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Fatalf("got %q, want %q", got, tc.want)
			}
		})
	}
}

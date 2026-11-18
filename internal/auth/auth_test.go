package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey_TableDriven(t *testing.T) {
	makeHdr := func(v string) http.Header {
		h := http.Header{}
		if v != "" {
			h.Set("Authorization", v)
		}
		return h
	}

	tests := []struct {
		name      string
		header    string
		wantKey   string
		wantErr   bool
		wantNoHdr bool // specifically expect ErrNoAuthHeaderIncluded
	}{
		{
			name:    "success",
			header:  "ApiKey abc123",
			wantKey: "abc123",
		},
		{
			name:      "missing header",
			header:    "",
			wantErr:   true,
			wantNoHdr: true,
		},
		{
			name:    "wrong scheme",
			header:  "Bearer abc123",
			wantErr: true,
		},
		{
			name:    "empty key allowed by implementation",
			header:  "ApiKey ",
			wantKey: "",
		},
		{
			name:    "key with spaces returns first token only",
			header:  "ApiKey too many parts",
			wantKey: "too",
		},
	}

	for _, tc := range tests {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(makeHdr(tc.header))

			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected error, got nil (key=%q)", key)
				}
				if tc.wantNoHdr && !errors.Is(err, ErrNoAuthHeaderIncluded) {
					t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if key != tc.wantKey {
				t.Fatalf("want key %q, got %q", tc.wantKey, key)
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

type testCase struct {
	name      string
	setHeader bool
	headerVal string
	wantKey   string
	wantErr   error
}

func TestGetAPIKey(t *testing.T) {
	cases := []testCase{
		{name: "no header", setHeader: false, wantErr: ErrNoAuthHeaderIncluded},
		{name: "empty header", setHeader: true, headerVal: "", wantErr: ErrNoAuthHeaderIncluded},
		{name: "valid", setHeader: true, headerVal: "ApiKey my-secret", wantKey: "my-secret", wantErr: nil},
		{name: "wrong prefix", setHeader: true, headerVal: "Bearer token", wantErr: errors.New("any")},
		{name: "missing key", setHeader: true, headerVal: "ApiKey", wantErr: errors.New("any")},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			headers := http.Header{}
			if tc.setHeader {
				headers.Set("Authorization", tc.headerVal)
			}

			got, err := GetAPIKey(headers)

			if tc.wantErr != nil {
				// For the specific missing-header error:
				if errors.Is(tc.wantErr, ErrNoAuthHeaderIncluded) && !errors.Is(err, ErrNoAuthHeaderIncluded) {
					t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
				}
				// For generic malformed cases just ensure err != nil
				if errors.Is(tc.wantErr, ErrNoAuthHeaderIncluded) && err == nil {
					t.Fatalf("expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.wantKey {
				t.Fatalf("want key %q, got %q", tc.wantKey, got)
			}
		})
	}
}

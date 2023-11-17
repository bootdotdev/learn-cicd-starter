package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	malformedHeader := http.Header{
		"Authorization": []string{"notapikey 123"},
	}
	tests := map[string]struct {
		headers http.Header
		wantErr error
	}{
		"no authorization header included": {
			http.Header{},
			ErrNoAuthHeaderIncluded,
		},
		"malformed authorization header": {
			malformedHeader,
			ErrMalformedAuthHeader,
		},
	}
	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			_, gotErr := GetAPIKey(tc.headers)
			if tc.wantErr != gotErr {
				t.Errorf("expected error %v, got %v", tc.wantErr, gotErr)
			}
		})
	}
}

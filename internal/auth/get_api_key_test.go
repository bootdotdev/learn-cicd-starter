package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		wantKey string
		wantErr error
	}{
		"valid api key": {
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantKey: "my-secret-key",
			wantErr: nil,
		},
		"no auth header": {
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		"malformed - wrong prefix": {
			headers: http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		"malformed - missing key": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.headers)

			if gotKey != tc.wantKey {
				t.Errorf("expected key %q, got %q", tc.wantKey, gotKey)
			}
			if (gotErr == nil) != (tc.wantErr == nil) {
				t.Errorf("expected error %v, got %v", tc.wantErr, gotErr)
				return
			}
			if gotErr != nil && gotErr.Error() != tc.wantErr.Error() {
				t.Errorf("expected error %q, got %q", tc.wantErr.Error(), gotErr.Error())
			}
		})
	}
}

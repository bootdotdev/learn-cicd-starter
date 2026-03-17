package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		wantKey   string
		wantError bool
		errMsg    string
	}{
		{
			name:      "missing authorization header",
			headers:   http.Header{},
			wantKey:   "",
			wantError: true,
			errMsg:    "no authorization header included",
		},
		{
			name:      "malformed header - wrong scheme",
			headers:   http.Header{"Authorization": []string{"Bearer some-token"}},
			wantKey:   "",
			wantError: true,
			errMsg:    "malformed authorization header",
		},
		{
			name:      "malformed header - only scheme",
			headers:   http.Header{"Authorization": []string{"ApiKey"}},
			wantKey:   "",
			wantError: true,
			errMsg:    "malformed authorization header",
		},
		{
			name:      "valid ApiKey header",
			headers:   http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantKey:   "my-secret-key",
			wantError: false,
		},
		{
			name:      "valid ApiKey with multiple spaces in key",
			headers:   http.Header{"Authorization": []string{"ApiKey my-secret-key-with-extra"}},
			wantKey:   "my-secret-key-with-extra",
			wantError: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			if (err != nil) != tc.wantError {
				t.Errorf("unexpected error state: got error=%v, wantError=%v", err != nil, tc.wantError)
			}

			if tc.wantError && err != nil && err.Error() != tc.errMsg {
				t.Errorf("wrong error message: got %q, want %q", err.Error(), tc.errMsg)
			}

			if key != tc.wantKey {
				t.Errorf("got key %q, want %q", key, tc.wantKey)
			}
		})
	}
}

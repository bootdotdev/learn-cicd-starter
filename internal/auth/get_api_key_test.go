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
		"no authorization header": {
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		"malformed - wrong scheme": {
			headers: http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		"malformed - missing key value": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		"malformed - empty header value": {
			headers: http.Header{"Authorization": []string{""}},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.headers)

			if gotKey != tc.wantKey {
				t.Errorf("key: got %q, want %q", gotKey, tc.wantKey)
			}

			switch {
			case tc.wantErr == nil && gotErr != nil:
				t.Errorf("error: got %q, want nil", gotErr)
			case tc.wantErr != nil && gotErr == nil:
				t.Errorf("error: got nil, want %q", tc.wantErr)
			case tc.wantErr != nil && gotErr.Error() != tc.wantErr.Error():
				t.Errorf("error: got %q, want %q", gotErr, tc.wantErr)
			}
		})
	}
}

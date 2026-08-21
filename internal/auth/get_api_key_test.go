package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		want    string
		wantErr error
	}{
		"valid api key": {
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			want:    "my-secret-key",
			wantErr: nil,
		},
		"no authorization header": {
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		"empty authorization header": {
			headers: http.Header{"Authorization": []string{""}},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		"wrong scheme": {
			headers: http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			want:    "",
			wantErr: ErrMalformedAuthHeader,
		},
		"missing key after scheme": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			wantErr: ErrMalformedAuthHeader,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			if tc.wantErr == nil && err != nil {
				t.Fatalf("GetAPIKey() unexpected error: %v", err)
			}
			if tc.wantErr != nil {
				if err == nil {
					t.Fatalf("GetAPIKey() expected error %v, got nil", tc.wantErr)
				}
				if !errors.Is(err, tc.wantErr) {
					t.Fatalf("GetAPIKey() error = %v, want %v", err, tc.wantErr)
				}
			}
			if got != tc.want {
				t.Errorf("GetAPIKey() = %q, want %q", got, tc.want)
			}
		})
	}
}

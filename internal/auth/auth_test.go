package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr error
	}{
		{
			name:    "no header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "wrong prefix",
			headers: http.Header{"Authorization": []string{"Bearer token"}},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name:    "missing token",
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name:    "valid key",
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			want:    "my-secret-key",
			wantErr: nil,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			// error assertion
			if tc.wantErr != nil {
				if err == nil || err.Error() != tc.wantErr.Error() {
					t.Fatalf("expected error %v, got %v", tc.wantErr, err)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			// value assertion
			if got != tc.want {
				t.Errorf("got %q, want %q", got, tc.want)
			}
		})
	}
}

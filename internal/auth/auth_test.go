package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		want      string
		wantError error
	}{
		{
			name:      "valid header",
			headers:   http.Header{"Authorization": {"ApiKey ABC123"}},
			want:      "ABC123",
			wantError: nil,
		},
		{
			name:      "no header",
			headers:   http.Header{},
			want:      "",
			wantError: ErrNoAuthHeaderIncluded,
		},
		{
			name:      "malformed header",
			headers:   http.Header{"Authorization": {"Bearer ABC123"}},
			want:      "",
			wantError: errors.New("malformed authorization header"),
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)
			if got != tc.want || (err != nil && err.Error() != tc.wantError.Error()) {
				t.Errorf("GetAPIKey() = %v, %v; want %v, %v", got, err, tc.want, tc.wantError)
			}
		})
	}
}

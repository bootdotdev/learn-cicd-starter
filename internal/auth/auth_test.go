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
			name:      "NoAuthorizationHeader",
			headers:   http.Header{},
			want:      "",
			wantError: ErrNoAuthHeaderIncluded,
		},
		{
			name:      "MalformedAuthorizationHeader",
			headers:   http.Header{"Authorization": []string{"Bearer token"}},
			want:      "",
			wantError: errors.New("malformed authorization header"),
		},
		{
			name:      "ValidAuthorizationHeader",
			headers:   http.Header{"Authorization": []string{"ApiKey some-valid-api-key"}},
			want:      "some-valid-api-key",
			wantError: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.want || (err != nil && err.Error() != tt.wantError.Error()) {
				t.Errorf("GetAPIKey() = %v, want %v, err = %v, wantError = %v", got, tt.want, err, tt.wantError)
			}

		})
	}
}

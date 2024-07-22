package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", errors.New("malformed authorization header")
	}

	return splitAuth[1], nil
}


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
			if got != tc.want || !errors.Is(err, tc.wantError) {
				t.Errorf("GetAPIKey() = %v, %v; want %v, %v", got, err, tc.want, tc.wantError)
			}
		})
	}
}
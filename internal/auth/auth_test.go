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
			name:    "Valid API key",
			headers: http.Header{"Authorization": []string{"ApiKey 12345"}},
			want:    "12345",
			wantErr: nil,
		},
		{
			name:    "Missing Authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "Malformed Authorization header",
			headers: http.Header{"Authorization": []string{"Bearer 12345"}},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.want || (err != nil && err.Error() != tt.wantErr.Error()) {
				t.Fatalf("Test %s failed: expected (%v, %v), got (%v, %v)", tt.name, tt.want, tt.wantErr, got, err)
			}
		})
	}
}

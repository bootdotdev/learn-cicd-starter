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
			name:    "no authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed authorization header",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "authorization header without api key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "valid authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			want:    "abc123",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}

			if err != nil && tt.wantErr == nil {
				t.Errorf("GetAPIKey() unexpected error = %v", err)
			}

			if err != nil && tt.wantErr != nil && err.Error() != tt.wantErr.Error() {
				t.Errorf("GetAPIKey() error = %v, want %v", err, tt.wantErr)
			}
		})
	}
}

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
			name:    "No Authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization header",
			headers: http.Header{
				"Authorization": []string{"InvalidHeader"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Authorization header (Wrong Prefix)",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "Valid API Key header",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			want:    "abc123",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)
			if key != tt.want || (err != nil && err.Error() != tt.wantErr.Error()) {
				t.Errorf("GetAPIKey() = %v, want: %v; error = %v, WantErr: %v", key, tt.want, err, tt.wantErr)
			}
		})
	}
}

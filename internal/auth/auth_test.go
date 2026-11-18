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
			name:    "Valid authorization header",
			headers: http.Header{"Authorization": []string{"ApiKey abc123"}},
			want:    "abc123",
			wantErr: nil,
		},
		{
			name:    "No authorization header included",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "Malformed authorization header",
			headers: http.Header{"Authorization": []string{"Bearer token"}},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}
			if (err != nil || tt.wantErr != nil) && err.Error() != tt.wantErr.Error() {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

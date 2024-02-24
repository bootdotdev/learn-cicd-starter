package auth

import (
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
			name:    "ValidApiKey",
			headers: http.Header{"Authorization": []string{"ApiKey myapikey"}},
			want:    "myapikey",
			wantErr: nil,
		},
		{
			name:    "NoAuthHeader",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "MalformedAuthHeader",
			headers: http.Header{"Authorization": []string{"Bearer token"}},
			want:    "",
			wantErr: ErrMalformedAuthHeader,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if err != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}
		})
	}
}

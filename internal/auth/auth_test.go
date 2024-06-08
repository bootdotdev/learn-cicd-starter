package auth // replace with your actual package name

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		want       string
		expectErr  bool
		errMessage string
	}{
		{
			name:       "No Authorization header",
			headers:    http.Header{},
			want:       "",
			expectErr:  true,
			errMessage: "no authorization header included",
		},
		{
			name:       "Authorization header missing ApiKey",
			headers:    http.Header{"Authorization": {"Bearer token"}},
			want:       "",
			expectErr:  true,
			errMessage: "malformed authorization header",
		},
		{
			name:      "Authorization header with ApiKey",
			headers:   http.Header{"Authorization": {"ApiKey myapikey"}},
			want:      "myapikey",
			expectErr: false,
		},
		{
			name:       "Malformed ApiKey header",
			headers:    http.Header{"Authorization": {"ApiKey"}},
			want:       "",
			expectErr:  true, // should be true
			errMessage: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.expectErr {
				t.Errorf("GetAPIKey() error = %v, expectErr %v", err, tt.expectErr)
				return
			}
			if err != nil && err.Error() != tt.errMessage {
				t.Errorf("GetAPIKey() error message = %v, wantErrMessage %v", err.Error(), tt.errMessage)
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}

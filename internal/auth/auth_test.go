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
		wantKey string
		wantErr error
	}{
		{
			name:    "missing authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "malformed authorization header - missing space",
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantKey: "",
			wantErr: ErrMalformedAuthHeader,
		},
		{
			name:    "malformed authorization header - wrong prefix",
			headers: http.Header{"Authorization": []string{"Bearer someapikey"}},
			wantKey: "",
			wantErr: ErrMalformedAuthHeader,
		},
		{
			name:    "correct authorization header",
			headers: http.Header{"Authorization": []string{"ApiKey someapikey"}},
			wantKey: "someapikey",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() gotKey = %v, want %v", gotKey, tt.wantKey)
			}
			if !errors.Is(err, tt.wantErr) {
				t.Errorf("GetAPIKey() err = %v, want %v", err, tt.wantErr)
			}
		})
	}
}

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
			name:    "No Authorization Header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer someapikey"},
			},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Header - missing API key value",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey correctapikey"},
			},
			wantKey: "correctapikey",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.wantKey {
				t.Errorf("GetAPIKey() returned key = %q, want %q", got, tt.wantKey)
			}
			// Compare error strings for equality.
			if (err == nil && tt.wantErr != nil) ||
				(err != nil && tt.wantErr == nil) ||
				(err != nil && tt.wantErr != nil && err.Error() != tt.wantErr.Error()) {
				t.Errorf("GetAPIKey() returned error = %v, want %v", err, tt.wantErr)
			}
		})
	}
}

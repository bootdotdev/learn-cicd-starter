package auth

import (
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
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey testkey123"},
			},
			wantKey: "testkey123",
			wantErr: nil,
		},
		{
			name:    "No authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// Check error
			if err != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// Check key
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() gotKey = %v, want %v", gotKey, tt.wantKey)
			}
		})
	}
}

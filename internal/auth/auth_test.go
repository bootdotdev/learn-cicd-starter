package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		wantKey   string
		wantError error
	}{
		{
			name:      "Missing Authorization Header",
			headers:   http.Header{},
			wantKey:   "",
			wantError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"InvalidHeader"},
			},
			wantKey:   "",
			wantError: errors.New("malformed authorization header"),
		},
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			wantKey:   "my-secret-key",
			wantError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			if gotKey != tt.wantKey {
				t.Errorf("expected key: %v, got: %v", tt.wantKey, gotKey)
			}

			if (err != nil && tt.wantError == nil) || (err == nil && tt.wantError != nil) || (err != nil && tt.wantError != nil && err.Error() != tt.wantError.Error()) {
				t.Errorf("expected error: %v, got: %v", tt.wantError, err)
			}
		})
	}
}

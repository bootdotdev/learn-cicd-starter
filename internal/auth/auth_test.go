// internal/auth/auth_test.go
package auth

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		header     http.Header
		wantAPIKey string
		wantErr    error
	}{
		{
			name:    "No API Key",
			header:  http.Header{},
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Valid API Key",
			header: http.Header{
				"Authorization": {"ApiKey valid-api-key"},
			},
			wantAPIKey: "valid-api-key",
			wantErr:    nil,
		},
		{
			name: "Invalid API Key Format",
			header: http.Header{
				"Authorization": {"invalid-api-key-format"},
			},
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "Wrong Auth Scheme",
			header: http.Header{
				"Authorization": {"Bearer valid-api-key"},
			},
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, "/", nil)
			req.Header = tt.header

			apiKey, err := GetAPIKey(req.Header)
			if err != nil && err.Error() != tt.wantErr.Error() {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if apiKey != tt.wantAPIKey {
				t.Errorf("GetAPIKey() = %v, want %v", apiKey, tt.wantAPIKey)
			}
		})
	}
}

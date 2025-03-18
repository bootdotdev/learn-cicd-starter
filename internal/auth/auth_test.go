package auth

import (
    "errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantAPIKey string
		wantErr    error
	}{
		{
			name:       "Valid API Key",
			headers:    http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantAPIKey: "my-secret-key",
			wantErr:    nil,
		},
		{
			name:       "No Authorization Header",
			headers:    http.Header{},
			wantAPIKey: "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name:       "Malformed Authorization Header",
			headers:    http.Header{"Authorization": []string{"InvalidHeader my-secret-key"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
		{
			name:       "Missing API Key Value",
			headers:    http.Header{"Authorization": []string{"ApiKey"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gotAPIKey, gotErr := GetAPIKey(tc.headers)

			if gotAPIKey != tc.wantAPIKey {
				t.Errorf("Expected API key %q, got %q", tc.wantAPIKey, gotAPIKey)
			}

			if (gotErr != nil && tc.wantErr == nil) || (gotErr == nil && tc.wantErr != nil) || (gotErr != nil && tc.wantErr != nil && gotErr.Error() != tc.wantErr.Error()) {
				t.Errorf("Expected error %v, got %v", tc.wantErr, gotErr)
			}
		})
	}
}

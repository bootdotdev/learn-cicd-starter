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
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			wantAPIKey: "my-secret-key",
			wantErr:    nil,
		},
		{
			name:       "Missing Authorization header",
			headers:    http.Header{},
			wantAPIKey: "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
		{
			name: "Incorrect prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-key"},
			},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotAPIKey, err := GetAPIKey(tt.headers)

			if gotAPIKey != tt.wantAPIKey {
				t.Errorf("GetAPIKey() got = %v, want %v", gotAPIKey, tt.wantAPIKey)
			}

			if err != nil && tt.wantErr != nil {
				if err.Error() != tt.wantErr.Error() {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.wantErr)
				}
			} else if err != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, want %v", err, tt.wantErr)
			}
		})
	}
}

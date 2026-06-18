package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantAPIKey string
		wantErr    bool
	}{
		{
			name:       "Valid API Key",
			headers:    http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantAPIKey: "wrong-key-goes-here",
			wantErr:    false,
		},
		{
			name:       "Missing Authorization Header",
			headers:    http.Header{},
			wantAPIKey: "",
			wantErr:    true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.wantAPIKey {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.wantAPIKey)
			}
		})
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		wantAPIKey  string
		wantErr     bool
	}{
		{
			name: "valid auth header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-api-key"},
			},
			wantAPIKey: "my-api-key",
			wantErr:    false,
		},
		{
			name: "missing auth header",
			headers: http.Header{},
			wantAPIKey: "",
			wantErr:    true,
		},
		{
			name: "malformed auth header",
			headers: http.Header{
				"Authorization": []string{"Invalid my-api-key"},
			},
			wantAPIKey: "",
			wantErr:    true,
		},
		{
			name: "empty auth header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			wantAPIKey: "",
			wantErr:    true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if apiKey != tt.wantAPIKey {
				t.Errorf("GetAPIKey() = %v, want %v", apiKey, tt.wantAPIKey)
			}
		})
	}
}
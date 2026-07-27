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
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey 1234567890"},
			},
			wantAPIKey: "1234567890",
			wantErr:    false,
		},
		{
			name: "Missing API key",
			headers: http.Header{
				"Authorization": []string{},
			},
			wantAPIKey: "",
			wantErr:    true,
		},
		{
			name: "Invalid API key format",
			headers: http.Header{
				"Authorization": []string{"Bearer 1234567890"},
			},
			wantAPIKey: "",
			wantErr:    true,
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(test.headers)
			if (err != nil) != test.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, test.wantErr)
			}
			if apiKey != test.wantAPIKey {
				t.Errorf("GetAPIKey() = %v, want %v", apiKey, test.wantAPIKey)
			}
		})
	}
}

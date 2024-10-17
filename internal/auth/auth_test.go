package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		wantedKey string
		expectErr bool
	}{
		{
			name: "Valid APIKey token",
			headers: http.Header{
				"Authorization": []string{"ApiKey valid_token"},
			},
			wantedKey: "valid_token",
			expectErr: false,
		},
		{
			name:      "Missing Authorization header",
			headers:   http.Header{},
			wantedKey: "",
			expectErr: true,
		},
		{
			name: "Malformed Authorization header",
			headers: http.Header{
				"Authorization": []string{"InvalidApiKey token"},
			},
			wantedKey: "",
			expectErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.expectErr {
				t.Errorf("GetAPIKey() error = %v, expectErr %v", err, tt.expectErr)
				return
			}
			if key != tt.wantedKey {
				t.Errorf("GetAPIKey() key = %v, want %v", key, tt.wantedKey)
			}
		})
	}

}

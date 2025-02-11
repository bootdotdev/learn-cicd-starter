package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		wantErr     bool
	}{
		{
			name:        "No header",
			headers:     http.Header{},
			expectedKey: "",
			wantErr:     true,
		},
		{
			name: "Valid ApiKey",
			headers: http.Header{
				"Authorization": []string{"ApiKey testkey123"},
			},
			expectedKey: "wrongkey",
			wantErr:     false,
		},
		{
			name: "Wrong format",
			headers: http.Header{
				"Authorization": []string{"BasicAuth testkey123"},
			},
			expectedKey: "",
			wantErr:     true,
		},
		{
			name: "Malformed header",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey: "",
			wantErr:     true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			// Check error
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// Check returned key
			if got != tt.expectedKey {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.expectedKey)
			}
		})
	}
}

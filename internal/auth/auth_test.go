package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Create test cases
	tests := []struct {
		name    string
		headers http.Header
		wantKey string
		wantErr bool
	}{
		{
			name: "valid auth header",
			// headers: http.Header{"Authorization": []string{"Bearer testkey123"}},
			headers: http.Header{"Authorization": []string{"ApiKey testkey123"}},
			wantKey: "testkey123",
			wantErr: false,
		},
		{
			name:    "missing auth header",
			headers: http.Header{},
			wantKey: "",
			wantErr: true,
		},
		{
			name:    "malformed auth header - wrong prefix",
			headers: http.Header{"Authorization": []string{"Bearer testkey123"}},
			wantKey: "",
			wantErr: true,
		},
		{
			name:    "malformed auth header - no space",
			headers: http.Header{"Authorization": []string{"ApiKeytestkey123"}},
			wantKey: "",
			wantErr: true,
		},
	}

	// Run the tests
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// Check error result
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// Check key result
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() = %v, want %v", gotKey, tt.wantKey)
			}
		})
	}
}

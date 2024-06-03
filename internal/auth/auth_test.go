package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr bool
	}{
		{"missing Authorization header", http.Header{}, "", true},
		{"malformed header without ApiKey", http.Header{"Authorization": {"123456"}}, "", true},
		{"correct Authorization header", http.Header{"Authorization": {"ApiKey 12345"}}, "12345", false},
		{"Authorization with multiple parts", http.Header{"Authorization": {"ApiKey 67890 12345"}}, "67890", false},
		{"case sensitive ApiKey", http.Header{"Authorization": {"apikey 67890"}}, "", true},
		{"multiple Authorization headers straightforward", http.Header{"Authorization": {"ApiKey 12345", "Bearer token"}}, "12345", false},
		{"multiple Authorization headers, ApiKey second", http.Header{"Authorization": {"Bearer token", "ApiKey 12345"}}, "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error - %s = %v, wantErr %v", tt.name, err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() - %s = %v, want %v", tt.name, got, tt.want)
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		wantAPIKey  string
		wantErr     error
	}{
		{
			name:        "valid api key",
			headers:     http.Header{"Authorization": []string{"ApiKey test-key"}},
			wantAPIKey:  "test-key",
			wantErr:     nil,
		},
		{
			name:        "missing auth header",
			headers:     http.Header{},
			wantAPIKey:  "",
			wantErr:     ErrNoAuthHeaderIncluded,
		},
		{
			name:        "malformed header - wrong prefix",
			headers:     http.Header{"Authorization": []string{"Bearer test-key"}},
			wantAPIKey:  "",
			wantErr:     errors.New("malformed authorization header"),
		},
		{
			name:        "malformed header - no key",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			wantAPIKey:  "",
			wantErr:     errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if tt.wantErr != nil && err.Error() != tt.wantErr.Error() {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.wantAPIKey {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.wantAPIKey)
			}
		})
	}
} 
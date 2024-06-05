package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers    http.Header
		wantAPIKey string
		wantErr    error
	}{
		"NoAuthHeader": {
			headers:    http.Header{},
			wantAPIKey: "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		"MalformedAuthHeader": {
			headers:    http.Header{"Authorization": {"Bearer"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
		"ValidAuthHeader": {
			headers:    http.Header{"Authorization": {"ApiKey 12345"}},
			wantAPIKey: "12345",
			wantErr:    nil,
		},
	}

	for name, tt := range tests {
		t.Run(name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)

			if apiKey != tt.wantAPIKey {
				t.Errorf("expected apiKey %v, got %v", tt.wantAPIKey, apiKey)
			}
			if (err != nil && tt.wantErr != nil &&
				(err.Error() != tt.wantErr.Error())) ||
				(err != nil && tt.wantErr == nil) ||
				(err == nil && tt.wantErr != nil) {
				t.Errorf("expected error %v, got %v", tt.wantErr, err)
			}
		})
	}
}

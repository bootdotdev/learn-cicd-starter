package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantKey    string
		wantErr    bool
		errMessage string
	}{
		{
			name:       "valid API key",
			headers:    http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantKey:    "my-secret-key",
			wantErr:    false,
			errMessage: "",
		},
		{
			name:       "missing Authorization header",
			headers:    http.Header{},
			wantKey:    "",
			wantErr:    true,
			errMessage: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:       "malformed Authorization header",
			headers:    http.Header{"Authorization": []string{"Bearer token"}},
			wantKey:    "",
			wantErr:    true,
			errMessage: "malformed authorization header",
		},
		{
			name:       "only keyword no key",
			headers:    http.Header{"Authorization": []string{"ApiKey"}},
			wantKey:    "",
			wantErr:    true,
			errMessage: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if err != nil && err.Error() != tt.errMessage {
				t.Errorf("GetAPIKey() error = %v, want %v", err, tt.errMessage)
			}
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() = %v, want %v", gotKey, tt.wantKey)
			}
		})
	}
}
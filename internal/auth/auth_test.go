package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantAPIKey string
		wantErr    error
	}{
		{
			name:       "No Authorization Header",
			headers:    http.Header{},
			wantAPIKey: "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name:       "Malformed Authorization Header",
			headers:    http.Header{"Authorization": {"Bearer abc123"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
		{
			name:       "Correct Authorization Header",
			headers:    http.Header{"Authorization": {"ApiKey abc123"}},
			wantAPIKey: "abc123",
			wantErr:    nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotAPIKey, gotErr := GetAPIKey(tt.headers)
			if gotAPIKey != tt.wantAPIKey {
				t.Errorf("GetAPIKey() gotAPIKey = %v, want %v", gotAPIKey, tt.wantAPIKey)
			}
			if (gotErr != nil && tt.wantErr == nil) || (gotErr == nil && tt.wantErr != nil) || (gotErr != nil && gotErr.Error() != tt.wantErr.Error()) {
				t.Errorf("GetAPIKey() gotErr = %v, want %v", gotErr, tt.wantErr)
			}
		})
	}
}

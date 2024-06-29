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
			name:       "No authorization header",
			headers:    http.Header{},
			wantAPIKey: "",
			wantErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name:       "Malformed authorization header",
			headers:    http.Header{"Authorization": []string{"Bearer someToken"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
		{
			name:       "Correct authorization header",
			headers:    http.Header{"Authorization": []string{"ApiKey myApiKey"}},
			wantAPIKey: "myApiKey",
			wantErr:    nil,
		},
		{
			name:       "Authorization header with extra spaces",
			headers:    http.Header{"Authorization": []string{" ApiKey myApiKey"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
		{
			name:       "Authorization header with wrong scheme",
			headers:    http.Header{"Authorization": []string{"ApiKeys myApiKey"}},
			wantAPIKey: "",
			wantErr:    errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotAPIKey, gotErr := GetAPIKey(tt.headers)
			if gotAPIKey != tt.wantAPIKey {
				t.Errorf("GetAPIKey() gotAPIKey = %v, want %v", gotAPIKey, tt.wantAPIKey)
			}
			if (gotErr != nil && tt.wantErr == nil) || (gotErr == nil && tt.wantErr != nil) {
				t.Errorf("GetAPIKey() gotErr = %v, want %v", gotErr, tt.wantErr)
			}
			if gotErr != nil && tt.wantErr != nil && gotErr.Error() != tt.wantErr.Error() {
				t.Errorf("GetAPIKey() gotErr = %v, want %v", gotErr, tt.wantErr)
			}
		})
	}
}


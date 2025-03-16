package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		wantKey       string
		wantErr       error
	}{
		{
			name: "valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey test-key-123"},
			},
			wantKey: "test-key-123",
			wantErr: nil,
		},
		{
			name:    "missing authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer test-key-123"},
			},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "malformed header - missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tt.headers)
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() key = %v, want %v", gotKey, tt.wantKey)
			}
			if (gotErr != nil) != (tt.wantErr != nil) || (gotErr != nil && gotErr.Error() != tt.wantErr.Error()) {
				t.Errorf("GetAPIKey() error = %v, want %v", gotErr, tt.wantErr)
			}
		})
	}
} 
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
		wantKey     string
		wantErr     error
		wantErrText string
	}{
		{
			name:    "Missing Authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Empty Authorization header value",
			headers: http.Header{
				"Authorization": []string{""},
			},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed header - missing ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer 12345"},
			},
			wantKey:     "",
			wantErrText: "malformed authorization header",
		},
		{
			name: "Malformed header - missing key component",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			wantKey:     "",
			wantErrText: "malformed authorization header",
		},
		{
			name: "Malformed header - invalid prefix casing",
			headers: http.Header{
				"Authorization": []string{"apikey 12345"},
			},
			wantKey:     "",
			wantErrText: "malformed authorization header",
		},
		{
			name: "Valid Authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key-123"},
			},
			wantKey: "my-secret-api-key-123",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// Check error expectations
			if tt.wantErr != nil {
				if !errors.Is(err, tt.wantErr) {
					t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				}
			} else if tt.wantErrText != "" {
				if err == nil || err.Error() != tt.wantErrText {
					t.Errorf("GetAPIKey() error = %v, wantErrText %q", err, tt.wantErrText)
				}
			} else if err != nil {
				t.Errorf("GetAPIKey() unexpected error = %v", err)
			}

			// Check key expectation
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() gotKey = %q, want %q", gotKey, tt.wantKey)
			}
		})
	}
}

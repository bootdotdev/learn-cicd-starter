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
		expectError error
	}{
		{
			name:        "no auth header",
			headers:     http.Header{},
			wantKey:     "",
			expectError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed header",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			wantKey:     "",
			expectError: errors.New("malformed authorization header"),
		},
		{
			name: "correct header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			wantKey:     "my-secret-key",
			expectError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			if gotKey != tt.wantKey {
				t.Errorf("got key = %v, want = %v", gotKey, tt.wantKey)
			}

			if err != nil && tt.expectError == nil {
				t.Errorf("got unexpected error: %v", err)
			} else if err == nil && tt.expectError != nil {
				t.Errorf("expected error but got none")
			} else if err != nil && tt.expectError != nil && err.Error() != tt.expectError.Error() {
				t.Errorf("expected error %v, got %v", tt.expectError, err)
			}
		})
	}
}

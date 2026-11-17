package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
		errorContains string
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key-123"},
			},
			expectedKey:   "my-secret-api-key-123",
			expectedError: nil,
		},
		{
			name:          "No Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Wrong Prefix (Bearer instead of ApiKey)",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-api-key-123"},
			},
			expectedKey:   "",
			errorContains: "malformed authorization header",
		},
		{
			name: "Malformed Header - Missing Token",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			errorContains: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// 1. Cek jika kita mengharapkan error spesifik (seperti ErrNoAuthHeaderIncluded)
			if tt.expectedError != nil {
				if !errors.Is(err, tt.expectedError) {
					t.Errorf("expected error %v, got %v", tt.expectedError, err)
				}
			} else if tt.errorContains != "" {
				// 2. Cek jika kita mengharapkan pesan error tertentu
				if err == nil || !strings.Contains(err.Error(), tt.errorContains) {
					t.Errorf("expected error containing %q, got %v", tt.errorContains, err)
				}
			} else if err != nil {
				// 3. Jika seharusnya tidak ada error tapi malah muncul error
				t.Errorf("unexpected error: %v", err)
			}

			// 4. Bandingkan hasil API Key yang didapat dengan ekspektasi
			if gotKey != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, gotKey)
			}
		})
	}
}

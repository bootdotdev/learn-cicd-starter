package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Create slice of test cases
	tests := []struct {
		name       string
		headers    http.Header
		wantKey    string
		expectErr  bool
		errMessage string
	}{
		//First test case: No Authorization Header
		{
			name:       "No Authorization Header",
			headers:    http.Header{}, // Empty headers
			expectErr:  true,
			errMessage: "no authorization header included",
		},
		//Second test case: Malformed Authorization Header - No Space
		{
			name: "Malformed Authorization Header - No Space",
			headers: http.Header{
				"Authorization": []string{"ApiKey12345"}, //http.Header in Go is defined as map[string][]string
			},
			expectErr:  true,
			errMessage: "malformed authorization header",
		},
		//Third test case: Malformed Authorization Header - Wrong Scheme
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"Bearer 12345"},
			},
			expectErr:  true,
			errMessage: "malformed authorization header",
		},
		//Fourth test case: Valid Authorization Header
		{
			name: "Valid Authorization Header",
			headers: http.Header{
				"Authorization": []string{"ApiKey 12345"},
			},
			wantKey:   "12345",
			expectErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.expectErr { // Check if error presence matches expectation (True/False)
				t.Errorf("GetAPIKey() error = %v, expectErr %v", err, tt.expectErr)
				return
			}
			if err != nil && !strings.Contains(err.Error(), tt.errMessage) { // Check if error message contains expected substring
				t.Errorf("GetAPIKey() error = %v, expected error message to contain %v", err, tt.errMessage)
			}
			if gotKey != tt.wantKey { // Check if returned key matches expected key
				t.Errorf("GetAPIKey() gotKey = %v, want %v", gotKey, tt.wantKey)
			}
		})
	}
}

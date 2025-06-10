package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError string
	}{
		{
			name: "valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			expectedKey:   "abc123",
			expectedError: "",
		},
		{
			name:          "missing authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: "no authorization header included",
		},
		{
			name: "empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey:   "",
			expectedError: "no authorization header included",
		},
		{
			name: "malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "malformed header - no key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "malformed header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKeyabc123"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			// Check the returned key
			if key != tt.expectedKey {
				t.Errorf("GetAPIKey() key = %v, want %v", key, tt.expectedKey)
			}

			// Check the error
			if tt.expectedError == "" {
				if err != nil {
					t.Errorf("GetAPIKey() error = %v, want nil", err)
				}
			} else {
				if err == nil {
					t.Errorf("GetAPIKey() error = nil, want %v", tt.expectedError)
				} else if err.Error() != tt.expectedError {
					t.Errorf("GetAPIKey() error = %v, want %v", err.Error(), tt.expectedError)
				}
			}
		})
	}
}

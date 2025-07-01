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
			name:          "No Authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: "no authorization header included",
		},
		{
			name:          "Empty Authorization header",
			headers:       http.Header{"Authorization": []string{""}},
			expectedKey:   "",
			expectedError: "no authorization header included",
		},
		{
			name:          "Malformed header - no space",
			headers:       http.Header{"Authorization": []string{"ApiKeytest123"}},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name:          "Malformed header - wrong prefix",
			headers:       http.Header{"Authorization": []string{"Bearer test123"}},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name:          "Malformed header - missing key",
			headers:       http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name:          "Valid header with empty key",
			headers:       http.Header{"Authorization": []string{"ApiKey "}},
			expectedKey:   "",
			expectedError: "",
		},
		{
			name:          "Valid header",
			headers:       http.Header{"Authorization": []string{"ApiKey test123"}},
			expectedKey:   "test123",
			expectedError: "",
		},
		{
			name:          "Valid header with complex key",
			headers:       http.Header{"Authorization": []string{"ApiKey abc-123-def-456"}},
			expectedKey:   "abc-123-def-456",
			expectedError: "",
		},
		{
			name:          "Valid header with extra parts",
			headers:       http.Header{"Authorization": []string{"ApiKey mykey extra parts"}},
			expectedKey:   "mykey",
			expectedError: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("GetAPIKey() key = %v, want %v", key, tt.expectedKey)
			}

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

func TestGetAPIKey_ErrNoAuthHeaderIncluded(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("GetAPIKey() should return ErrNoAuthHeaderIncluded for missing header, got %v", err)
	}
}

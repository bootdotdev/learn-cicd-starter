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
			name: "valid api key",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123def456"},
			},
			expectedKey:   "abc123def456",
			expectedError: "",
		},
		{
			name: "valid api key with multiple parts",
			headers: http.Header{
				"Authorization": []string{"ApiKey key-with-dashes-and-numbers-123"},
			},
			expectedKey:   "key-with-dashes-and-numbers-123",
			expectedError: "",
		},
		{
			name:          "missing authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "malformed header - missing ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "malformed header - wrong case",
			headers: http.Header{
				"Authorization": []string{"apikey abc123"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "malformed header - only ApiKey without value",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: "malformed authorization header",
		},
		{
			name: "malformed header - only ApiKey with space but no value",
			headers: http.Header{
				"Authorization": []string{"ApiKey "},
			},
			expectedKey:   "",
			expectedError: "",
		},
		{
			name: "authorization header with extra content after key",
			headers: http.Header{
				"Authorization": []string{"ApiKey mykey extra content here"},
			},
			expectedKey:   "mykey",
			expectedError: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.expectedError != "" {
				if err == nil {
					t.Errorf("expected error '%s', got nil", tt.expectedError)
					return
				}
				if err.Error() != tt.expectedError {
					t.Errorf("expected error '%s', got '%s'", tt.expectedError, err.Error())
				}
			} else {
				if err != nil {
					t.Errorf("expected no error, got '%s'", err.Error())
				}
			}

			if key != tt.expectedKey {
				t.Errorf("expected key '%s', got '%s'", tt.expectedKey, key)
			}
		})
	}
}

func TestGetAPIKey_CaseInsensitiveHeader(t *testing.T) {
	// Test that HTTP header names are case-insensitive
	headers := http.Header{}
	headers.Set("authorization", "ApiKey test123") // lowercase header name

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("expected no error, got '%s'", err.Error())
	}
	if key != "test123" {
		t.Errorf("expected key 'test123', got '%s'", key)
	}
}

func TestGetAPIKey_MultipleAuthHeaders(t *testing.T) {
	// Test behavior when multiple Authorization headers are present
	headers := http.Header{
		"Authorization": []string{"ApiKey first123", "ApiKey second456"},
	}

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("expected no error, got '%s'", err.Error())
	}
	// http.Header.Get() returns the first value
	if key != "first123" {
		t.Errorf("expected key 'first123', got '%s'", key)
	}
}

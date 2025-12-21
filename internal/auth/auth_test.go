package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedKey    string
		expectedError  error
		expectedErrMsg string
	}{
		{
			name:          "missing authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "valid ApiKey header",
			headers: http.Header{
				"Authorization": []string{"ApiKey test-api-key-123"},
			},
			expectedKey:   "test-api-key-123",
			expectedError: nil,
		},
		{
			name: "valid ApiKey header with long key",
			headers: http.Header{
				"Authorization": []string{"ApiKey very-long-api-key-with-many-characters-123456789"},
			},
			expectedKey:   "very-long-api-key-with-many-characters-123456789",
			expectedError: nil,
		},
		{
			name: "malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer token123"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "malformed header - missing space",
			headers: http.Header{
				"Authorization": []string{"ApiKeytest-key"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "malformed header - only prefix",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "ApiKey prefix with trailing space returns empty key",
			headers: http.Header{
				"Authorization": []string{"ApiKey "},
			},
			expectedKey:   "",
			expectedError: nil,
		},
		{
			name: "ApiKey with multiple spaces returns first token only",
			headers: http.Header{
				"Authorization": []string{"ApiKey key with spaces"},
			},
			expectedKey:   "key",
			expectedError: nil,
		},
		{
			name: "case sensitive ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"apikey test-key"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "case sensitive ApiKey prefix - mixed case",
			headers: http.Header{
				"Authorization": []string{"APIKEY test-key"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}

			if tt.expectedError != nil {
				if !errors.Is(err, tt.expectedError) {
					t.Errorf("expected error %v, got %v", tt.expectedError, err)
				}
			} else if tt.expectedErrMsg != "" {
				if err == nil {
					t.Errorf("expected error with message %q, got nil", tt.expectedErrMsg)
				} else if err.Error() != tt.expectedErrMsg {
					t.Errorf("expected error message %q, got %q", tt.expectedErrMsg, err.Error())
				}
			} else {
				if err != nil {
					t.Errorf("expected no error, got %v", err)
				}
			}
		})
	}
}

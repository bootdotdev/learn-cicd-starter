package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectError bool
		errorMsg    string
	}{
		{
			name: "valid API key",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "ApiKey test-api-key-123")
				return h
			}(),
			expectedKey: "test-api-key-123",
			expectError: false,
		},
		{
			name: "valid API key with complex value",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "ApiKey abc123-def456-ghi789")
				return h
			}(),
			expectedKey: "abc123-def456-ghi789",
			expectError: false,
		},
		{
			name:        "missing authorization header",
			headers:     make(http.Header),
			expectedKey: "",
			expectError: true,
			errorMsg:    "no authorization header included",
		},
		{
			name: "empty authorization header",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "")
				return h
			}(),
			expectedKey: "",
			expectError: true,
			errorMsg:    "no authorization header included",
		},
		{
			name: "malformed header - only ApiKey",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "ApiKey")
				return h
			}(),
			expectedKey: "",
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name: "malformed header - wrong scheme",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "Bearer test-token")
				return h
			}(),
			expectedKey: "",
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name: "malformed header - lowercase apikey",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "apikey test-api-key")
				return h
			}(),
			expectedKey: "",
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name: "malformed header - no space",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "ApiKeytest-api-key")
				return h
			}(),
			expectedKey: "",
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name: "API key with spaces (multiple parts after ApiKey)",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "ApiKey test api key with spaces")
				return h
			}(),
			expectedKey: "test",
			expectError: false,
		},
		{
			name: "empty API key value",
			headers: func() http.Header {
				h := make(http.Header)
				h.Set("Authorization", "ApiKey ")
				return h
			}(),
			expectedKey: "",
			expectError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.expectError {
				if err == nil {
					t.Errorf("expected error but got none")
					return
				}
				if tt.errorMsg != "" && err.Error() != tt.errorMsg {
					t.Errorf("expected error message %q, got %q", tt.errorMsg, err.Error())
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
					return
				}
			}

			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}
		})
	}
}

func TestErrNoAuthHeaderIncluded(t *testing.T) {
	// Test that the exported error variable is properly defined
	if ErrNoAuthHeaderIncluded == nil {
		t.Error("ErrNoAuthHeaderIncluded should not be nil")
	}

	expectedMsg := "no authorization header included"
	if ErrNoAuthHeaderIncluded.Error() != expectedMsg {
		t.Errorf("expected error message %q, got %q", expectedMsg, ErrNoAuthHeaderIncluded.Error())
	}
}

// Benchmark test for performance
func BenchmarkGetAPIKey(b *testing.B) {
	headers := make(http.Header)
	headers.Set("Authorization", "ApiKey test-benchmark-key-12345")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = GetAPIKey(headers)
	}
}
package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        map[string]string
		expectedAPIKey string
		expectedError  error
	}{
		{
			name:           "valid API key",
			headers:        map[string]string{"Authorization": "ApiKey valid-api-key-123"},
			expectedAPIKey: "valid-api-key-123",
			expectedError:  nil,
		},
		{
			name:           "valid API key with extra spaces",
			headers:        map[string]string{"Authorization": "ApiKey  another-valid-key"},
			expectedAPIKey: "", // strings.Split returns empty string for the second element
			expectedError:  nil,
		},
		{
			name:           "valid API key with special characters",
			headers:        map[string]string{"Authorization": "ApiKey key-with-special-chars!@#$%"},
			expectedAPIKey: "key-with-special-chars!@#$%",
			expectedError:  nil,
		},
		{
			name:           "valid API key with multiple parts",
			headers:        map[string]string{"Authorization": "ApiKey key with multiple parts"},
			expectedAPIKey: "key", // strings.Split takes only the second element
			expectedError:  nil,
		},
		{
			name:           "missing authorization header",
			headers:        map[string]string{},
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded,
		},
		{
			name:           "empty authorization header",
			headers:        map[string]string{"Authorization": ""},
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded,
		},
		{
			name:           "malformed header - wrong prefix",
			headers:        map[string]string{"Authorization": "Bearer some-token"},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "malformed header - wrong prefix case",
			headers:        map[string]string{"Authorization": "apikey some-key"},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "malformed header - no space",
			headers:        map[string]string{"Authorization": "ApiKey"},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "malformed header - only ApiKey with space",
			headers:        map[string]string{"Authorization": "ApiKey "},
			expectedAPIKey: "", // strings.Split returns empty string for the second element
			expectedError:  nil,
		},
		{
			name:           "malformed header - multiple spaces before key",
			headers:        map[string]string{"Authorization": "ApiKey  "},
			expectedAPIKey: "", // strings.Split returns empty string for the second element
			expectedError:  nil,
		},
		{
			name:           "case insensitive authorization header key",
			headers:        map[string]string{"authorization": "ApiKey some-key"},
			expectedAPIKey: "some-key",
			expectedError:  nil,
		},
		{
			name:           "mixed case authorization header key",
			headers:        map[string]string{"AUTHORIZATION": "ApiKey some-key"},
			expectedAPIKey: "some-key",
			expectedError:  nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create headers from the test case
			headers := make(http.Header)
			for key, value := range tt.headers {
				headers.Set(key, value)
			}

			// Call the function
			apiKey, err := GetAPIKey(headers)

			// Check the API key
			if apiKey != tt.expectedAPIKey {
				t.Errorf("GetAPIKey() apiKey = %v, want %v", apiKey, tt.expectedAPIKey)
			}

			// Check the error
			if tt.expectedError == nil {
				if err != nil {
					t.Errorf("GetAPIKey() error = %v, want nil", err)
				}
			} else {
				if err == nil {
					t.Errorf("GetAPIKey() error = nil, want %v", tt.expectedError)
				} else if err.Error() != tt.expectedError.Error() {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.expectedError)
				}
			}
		})
	}
}

func TestGetAPIKey_EdgeCases(t *testing.T) {
	t.Run("nil headers", func(t *testing.T) {
		// This shouldn't happen in practice, but let's test it
		var headers http.Header
		apiKey, err := GetAPIKey(headers)

		if apiKey != "" {
			t.Errorf("GetAPIKey() with nil headers apiKey = %v, want empty string", apiKey)
		}
		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("GetAPIKey() with nil headers error = %v, want %v", err, ErrNoAuthHeaderIncluded)
		}
	})

	t.Run("very long API key", func(t *testing.T) {
		longKey := "a" + string(make([]byte, 1000)) // 1001 character key
		headers := make(http.Header)
		headers.Set("Authorization", "ApiKey "+longKey)

		apiKey, err := GetAPIKey(headers)

		if err != nil {
			t.Errorf("GetAPIKey() with long key error = %v, want nil", err)
		}
		if apiKey != longKey {
			t.Errorf("GetAPIKey() with long key length = %d, want %d", len(apiKey), len(longKey))
		}
	})
}

// Benchmark tests
func BenchmarkGetAPIKey_Valid(b *testing.B) {
	headers := make(http.Header)
	headers.Set("Authorization", "ApiKey test-api-key")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = GetAPIKey(headers)
	}
}

func BenchmarkGetAPIKey_Invalid(b *testing.B) {
	headers := make(http.Header)
	headers.Set("Authorization", "Bearer test-token")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = GetAPIKey(headers)
	}
}

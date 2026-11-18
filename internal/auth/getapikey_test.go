package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		name            string
		headers         http.Header
		expectedKey     string
		expectedError   error
		shouldHaveError bool
	}{
		{
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key"},
			},
			expectedKey:     "my-secret-api-key",
			expectedError:   nil,
			shouldHaveError: false,
		},
		{
			name:            "No authorization header",
			headers:         http.Header{},
			expectedKey:     "",
			expectedError:   ErrNoAuthHeaderIncluded,
			shouldHaveError: true,
		},
		{
			name: "Empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey:     "",
			expectedError:   ErrNoAuthHeaderIncluded,
			shouldHaveError: true,
		},
		{
			name: "Malformed header - only ApiKey",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:     "",
			expectedError:   nil, // We'll check error message instead
			shouldHaveError: true,
		},
		{
			name: "Malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer my-token"},
			},
			expectedKey:     "",
			expectedError:   nil, // We'll check error message instead
			shouldHaveError: true,
		},
		{
			name: "Malformed header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKeymy-secret-key"},
			},
			expectedKey:     "",
			expectedError:   nil, // We'll check error message instead
			shouldHaveError: true,
		},
		{
			name: "API key with extra spaces - returns empty string",
			headers: http.Header{
				"Authorization": []string{"ApiKey  my-secret-api-key"},
			},
			expectedKey:     "", // Split results in empty string at index 1
			expectedError:   nil,
			shouldHaveError: false, // No error is actually thrown
		},
		{
			name: "API key with multiple parts",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key-with-dashes"},
			},
			expectedKey:     "my-secret-api-key-with-dashes",
			expectedError:   nil,
			shouldHaveError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.shouldHaveError {
				if err == nil {
					t.Errorf("Expected an error but got none")
					return
				}

				// Check for specific error types
				if tt.expectedError != nil && err != tt.expectedError {
					t.Errorf("Expected error %v, got %v", tt.expectedError, err)
				}

				// For malformed header errors, check the error message
				if tt.expectedError == nil && err.Error() != "malformed authorization header" {
					t.Errorf("Expected 'malformed authorization header' error, got %v", err)
				}
			} else {
				if err != nil {
					t.Errorf("Expected no error but got: %v", err)
				}
			}

			if key != tt.expectedKey {
				t.Errorf("Expected key %q, got %q", tt.expectedKey, key)
			}
		})
	}
}

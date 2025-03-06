package auth

import (
	"errors"
	"net/http"
	"testing"
)

// Helper function to create an http.Header with the Authorization header.
func createHeader(authHeader string) http.Header {
	headers := make(http.Header)
	if authHeader != "" {
		headers.Add("Authorization", authHeader)
	}
	return headers
}

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedAPIKey string
		expectedError  error
	}{
		{
			name:           "No Authorization header",
			headers:        createHeader(""),
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded,
		},
		{
			name:           "Malformed Authorization header",
			headers:        createHeader("ApiKey"), // Missing the API key after "ApiKey"
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "Valid Authorization header",
			headers:        createHeader("ApiKey abc123"),
			expectedAPIKey: "abc123",
			expectedError:  nil,
		},
		{
			name:           "Authorization header with wrong scheme",
			headers:        createHeader("Bearer abc123"),
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "Authorization header with extra parts",
			headers:        createHeader("ApiKey abc123 extra stuff"),
			expectedAPIKey: "abc123", // Should only take the first part after "ApiKey"
			expectedError:  nil,
		},
		{
			name:           "Authorization header with tab character",
			headers:        createHeader("ApiKey\tabc123"),
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if apiKey != tt.expectedAPIKey {
				t.Errorf("expected API key %v, got %v", tt.expectedAPIKey, apiKey)
			}

			if err != nil && err.Error() != tt.expectedError.Error() {
				t.Errorf("expected error %v, got %v", tt.expectedError, err)
			} else if err == nil && tt.expectedError != nil {
				t.Errorf("expected error %v, got nil", tt.expectedError)
			}
		})
	}
}

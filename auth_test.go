package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedAPIKey string
		expectedError  error
	}{
		{
			name:           "Valid API Key",
			headers:        http.Header{"Authorization": []string{"ApiKey my-api-key"}},
			expectedAPIKey: "my-api-key",
			expectedError:  nil,
		},
		{
			name:           "Missing Authorization Header",
			headers:        http.Header{},
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded,
		},
		{
			name:           "Malformed Authorization Header - Missing ApiKey",
			headers:        http.Header{"Authorization": []string{"Bearer my-api-key"}},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "Malformed Authorization Header - No Key",
			headers:        http.Header{"Authorization": []string{"ApiKey"}},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name:           "Empty Authorization Header",
			headers:        http.Header{"Authorization": []string{""}},
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)

			// Check if API key matches expectation
			if apiKey != tt.expectedAPIKey {
				t.Errorf("expected API key %q, got %q", tt.expectedAPIKey, apiKey)
			}

			// Check if error matches expectation
			if (err != nil && tt.expectedError == nil) || (err == nil && tt.expectedError != nil) {
				t.Errorf("expected error %v, got %v", tt.expectedError, err)
			} else if err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error() {
				t.Errorf("expected error %q, got %q", tt.expectedError.Error(), err.Error())
			}
		})
	}
}
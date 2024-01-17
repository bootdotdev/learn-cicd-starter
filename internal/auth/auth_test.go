package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name:          "ValidApiKeyHeader",
			headers:       http.Header{"Authorization": []string{"ApiKey test-api-key"}},
			expectedKey:   "test-api-key",
			expectedError: nil,
		},
		{
			name:          "NoAuthorizationHeader",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "MalformedAuthorizationHeader",
			headers:       http.Header{"Authorization": []string{"InvalidHeader"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "IncompleteAuthorizationHeader",
			headers:       http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)

			if key != test.expectedKey {
				t.Errorf("Expected key %s, got %s", test.expectedKey, key)
			}

			if err != nil && test.expectedError != nil && err.Error() != test.expectedError.Error() {
				t.Errorf("Expected error %v, got %v", test.expectedError, err)
			}

			if err == nil && test.expectedError != nil {
				t.Errorf("Expected error %v, got nil", test.expectedError)
			}

			if err != nil && test.expectedError == nil {
				t.Errorf("Expected no error, got %v", err)
			}
		})
	}
}

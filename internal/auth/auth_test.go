package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectedErr error
	}{
		{
			name:        "Valid ApiKey header",
			headers:     http.Header{"Authorization": []string{"ApiKey abc123"}},
			expectedKey: "abc123",
			expectedErr: nil,
		},
		{
			name:        "Missing Authorization header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "Malformed Authorization header",
			headers:     http.Header{"Authorization": []string{"Bearer abc123"}},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "Authorization header with no ApiKey value",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)

			// Check the API key
			if key != test.expectedKey {
				t.Errorf("expected key %q, got %q", test.expectedKey, key)
			}

			// Check the error
			if test.expectedErr == nil && err != nil {
				t.Errorf("expected no error, got %v", err)
			} else if test.expectedErr != nil && (err == nil || err.Error() != test.expectedErr.Error()) {
				t.Errorf("expected error %v, got %v", test.expectedErr, err)
			}
		})
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		"valid api key": {
			headers: http.Header{
				"Authorization": []string{"ApiKey abcd1234"},
			},
			expectedKey:   "abcd1234",
			expectedError: nil,
		},
		"no auth header": {
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		"malformed header - missing ApiKey prefix": {
			headers: http.Header{
				"Authorization": []string{"abcd1234"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		"malformed header - empty after prefix": {
			headers: http.Header{
				"Authorization": []string{"ApiKey "},
			},
			expectedKey:   "",
			expectedError: nil,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			// Compare the key using cmp.Diff
			if diff := cmp.Diff(tc.expectedKey, key); diff != "" {
				t.Errorf("key mismatch (-want +got):\n%s", diff)
			}

			// For errors, we might use a custom comparison
			if (tc.expectedError == nil) != (err == nil) {
				t.Errorf("error existence mismatch: expected %v, got %v", tc.expectedError, err)
			} else if tc.expectedError != nil && err != nil {
				// If both errors exist, compare their messages
				if tc.expectedError.Error() != err.Error() {
					t.Errorf("error mismatch: expected %v, got %v", tc.expectedError, err)
				}
			}
		})
	}
}

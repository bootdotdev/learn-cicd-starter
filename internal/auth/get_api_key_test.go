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
			name:        "no authorization header",
			headers:     http.Header{},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "valid api key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			expectedKey: "wrong-key",
			expectedErr: nil,
		},
		{
			name: "malformed header missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "malformed header wrong scheme",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-key"},
			},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "empty authorization header value",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			if key != tc.expectedKey {
				t.Errorf("expected key %q, got %q", tc.expectedKey, key)
			}

			if tc.expectedErr == nil && err != nil {
				t.Errorf("expected no error, got %v", err)
			}
			if tc.expectedErr != nil && err == nil {
				t.Errorf("expected error %v, got nil", tc.expectedErr)
			}
			if tc.expectedErr != nil && err != nil && err.Error() != tc.expectedErr.Error() {
				t.Errorf("expected error %q, got %q", tc.expectedErr.Error(), err.Error())
			}
		})
	}
}

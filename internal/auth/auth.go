package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", errors.New("malformed authorization header")
	}

	return splitAuth[1], nil
}

func TestGetAPIKey(t *testing.T) {
	testCases := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "valid api key",
			headers: func() http.Header {
				h := make(http.Header)
				h.Add("Authorization", "ApiKey test-key")
				return h
			}(),
			expectedKey:   "test-key",
			expectedError: nil,
		},
		{
			name:          "missing authorization header",
			headers:       make(http.Header),
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed header",
			headers: func() http.Header {
				h := make(http.Header)
				h.Add("Authorization", "Bearer wrong-format")
				return h
			}(),
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)
			if key != tc.expectedKey {
				t.Errorf("expected key %q, got %q", tc.expectedKey, key)
			}
			if err != nil && err.Error() != tc.expectedError.Error() {
				t.Errorf("expected error %q, got %q", tc.expectedError, err)
			}
		})
	}
}

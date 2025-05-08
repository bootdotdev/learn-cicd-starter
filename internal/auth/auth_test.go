package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		header http.Header
		apiKey string
		err    error
	}{
		"simple": {
			header: http.Header{
				"Authorization": {"ApiKey abcde"},
			},
			apiKey: "abcde",
			err:    nil,
		},

		"missing_auth_header": {
			header: http.Header{
				"Content-Type": {"application/json"},
			},
			apiKey: "",
			err:    ErrNoAuthHeaderIncluded,
		},

		"insufficient_length": {
			header: http.Header{
				"Authorization": {"ApiKey"},
			},
			apiKey: "",
			err:    ErrMalformedAuthHeader,
		},

		"wrong_prefix": {
			header: http.Header{
				"Authorization": {"API_KEY"},
			},
			apiKey: "",
			err:    ErrMalformedAuthHeader,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, actualErr := GetAPIKey(tc.header)

			if actualErr != nil && actualErr != tc.err {
				t.Fatalf("Wrong error: %v; should be %v", actualErr, tc.err)
			}

			if got != tc.apiKey {
				t.Fatalf("Wrong API key result: %v; should be %v", got, tc.apiKey)
			}
		})
	}
}

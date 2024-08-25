package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  error
	}{
		"no authorization header": {http.Header{}, ErrNoAuthHeaderIncluded},
		"no api key": {
			http.Header{
				"Authorization": []string{"1234"},
			},
			ErrMalformedAuthHeader,
		},
		"malformed api key": {
			http.Header{
				"Authorization": []string{"ApiKey"},
			},
			ErrMalformedAuthHeader,
		},
		"api key supplied": {
			http.Header{
				"Authorization": []string{"ApiKey 1234"},
			},
			nil,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			_, err := GetAPIKey(tc.input)
			if !errors.Is(err, tc.want) {
				t.Fatalf("expected: %v got: %v\n", tc.want, err)
			}
		})
	}
}

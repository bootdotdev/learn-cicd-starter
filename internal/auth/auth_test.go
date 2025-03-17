package auth

import (
	"errors"
	"net/http"
	"testing"
)

type apiKeyResult struct {
	ApiKey string
	err    error
}

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  apiKeyResult
	}{
		"Simple": {
			input: func() http.Header {
				h := http.Header{}
				h.Add("Authorization", "ApiKey test-key")
				return h
			}(),
			want: apiKeyResult{"test-key", nil}},
		"NoAuthHeader": {
			input: func() http.Header {
				h := http.Header{}
				return h
			}(),
			want: apiKeyResult{"", ErrNoAuthHeaderIncluded}},
		"MalformedAuthHeader": {
			input: func() http.Header {
				h := http.Header{}
				h.Add("Authorization", "Badformay")
				return h
			}(),
			want: apiKeyResult{"", errors.New("malformed authorization header")}},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			if got != tc.want.ApiKey {
				t.Errorf("expected API key: %v, got: %v", tc.want.ApiKey, got)
			}
			if err == nil && tc.want.err == nil {
				// both nil, that's good
			} else if err == nil || tc.want.err == nil {
				t.Errorf("expected error: %v, got: %v", tc.want.err, err)
			} else if err.Error() != tc.want.err.Error() {
				t.Errorf("expected error: %v, got: %v", tc.want.err, err)
			}
		})
	}

}

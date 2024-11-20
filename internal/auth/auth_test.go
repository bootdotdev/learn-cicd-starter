package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	type test struct {
		input http.Header
		want  string
		err   error
	}

	testCases := []test{
		{input: http.Header{"Authorization": []string{"ApiKey api-key"}}, want: "api-key"},
		{input: http.Header{"Authorization": []string{"test api-key"}}, want: "", err: errors.New("malformed authorization header")},
		{input: http.Header{}, want: "", err: ErrNoAuthHeaderIncluded},
	}

	for _, tc := range testCases {
		got, err := GetAPIKey(tc.input)
		if tc.err != nil && err.Error() != tc.err.Error() {
			t.Fatalf("Expected error: %v, got: %v", tc.err, err)
		}

		if got != tc.want {
			t.Fatalf("Expected: %s, got: %s", tc.want, got)
		}
	}

}

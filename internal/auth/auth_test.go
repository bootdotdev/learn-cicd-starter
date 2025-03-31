package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		input    string
		expected string
		err      error
	}{
		{input: "", expected: "", err: ErrNoAuthHeaderIncluded},
		{input: "Apikey", expected: "", err: ErrMalformedAuthHeader},
		{input: "Bearer token", expected: "", err: ErrMalformedAuthHeader},
		{input: "ApiKey some_ke", expected: "some_key", err: nil},
	}

	for _, tc := range tests {
		headers := make(http.Header)
		headers["Authorization"] = []string{tc.input}

		actual, err := GetAPIKey(headers)
		if !reflect.DeepEqual(tc.expected, actual) {
			t.Fatalf("expected: %v, got: %v", tc.expected, actual)
		}

		if tc.err != err {
			t.Fatalf("expected %v, got: %v", tc.err, err)
		}
	}
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input       string
		description string
		wantErr     error
		expect      string
	}

	tests := []test{
		{
			input:       "ApiKey key",
			description: "Key Present",
			wantErr:     nil,
			expect:      "key",
		},
		{
			input:       "",
			description: "Want Error",
			wantErr:     ErrNoAuthHeaderIncluded,
			expect:      "",
		},
		{
			input:       "Junk",
			description: "Want Malformed ",
			wantErr:     ErrMalformedAuthHeader,
			expect:      "",
		},
	}

	httpHeaders := http.Header{}
	for _, test := range tests {
		Cleanup(httpHeaders)
		if test.input != "" {
			Setup(httpHeaders, test.input)
		}

		result, err := GetAPIKey(httpHeaders)
		if test.wantErr != nil && err != test.wantErr {
			t.Fatalf("test %s: expected: %v, got: %v", test.description, test.wantErr, err)
		}

		if test.wantErr == nil && result != test.expect {
			t.Fatalf("test %s: expected: %s, got: %v", test.description, test.expect, result)
		}
	}
}

func Setup(headers http.Header, content string) {
	headers.Set("Authorization", content)
}

func Cleanup(headers http.Header) {
	headers.Del("Authorization")
}

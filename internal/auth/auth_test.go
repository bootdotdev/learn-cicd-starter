package auth

import (
	"net/http"
	"testing"
)

func TestApiKeyGetter(t *testing.T) {
	type test struct {
		input  string
		output string
		error  error
	}

	h := http.Header{}

	tests := []test{
		{input: "", output: "", error: ErrNoAuthHeaderIncluded},
		{input: "fake Api key", output: "", error: MalformedAuthError},
		{input: "ApiKey this-is-a-real-api-key", output: "this-is-a-real-api key", error: nil},
	}

	for _, testCase := range tests {
		h.Set("Authorization", testCase.input)

		output, error := GetAPIKey(h)

		if output != testCase.output {
			t.Fatalf("Output is wrong! \nexpected: %v, got: %v\n", testCase.output, output)
		} else if error != testCase.error {
			t.Fatalf("Error is wrong! \nexpected: %v, got: %v\n", testCase.error, error)
		}
	}
}

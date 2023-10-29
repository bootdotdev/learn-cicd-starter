package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestSplit(t *testing.T) {

	cases := []struct {
		input  http.Header
		output string
		Error  error
	}{
		{
			input:  http.Header{"Authorization": []string{"ApiKey fuck-you"}},
			output: "fuck-you",
			Error:  nil,
		},
		{
			input:  http.Header{"Authorization": []string{"ApiKey"}},
			output: "",
			Error:  ErrNoAuthHeaderIncluded,
		},

		{
			input:  http.Header{"Authorization": []string{""}},
			output: "",
			Error:  errors.New("malformed authorization header"),
		},

		{
			input:  http.Header{"Authorization": []string{"fuck-you"}},
			output: "",
			Error:  errors.New("malformed authorization header"),
		},
	}

	for i, tc := range cases {
		got, _ := GetAPIKey(tc.input)
		want := tc.output

		if got != want {
			t.Errorf("Error in test case %v", i)
		}

	}

}

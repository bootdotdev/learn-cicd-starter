package auth

import (
	"errors"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	type want struct {
		result string
		err    error
	}

	type test struct {
		name  string
		input map[string][]string
		want  want
	}

	var tests = []test{

		{
			name:  "1. Correct Authorization header",
			input: map[string][]string{"Authorization": {"ApiKey 1234"}},
			want: want{
				result: "1234",
				err:    nil,
			},
		},
		{
			name:  "2. Invalid Auth Header Key",
			input: map[string][]string{"Authorizations": {"ApiKey 1234"}},
			want: want{
				result: "",
				err:    ErrNoAuthHeaderIncluded,
			},
		},
		{
			name:  "3. Invalid Auth Value Size",
			input: map[string][]string{"Authorization": {"abcd1234"}},
			want: want{
				result: "",
				err:    ErrMalformedAuthHeaderIncluded,
			},
		},

		{
			name:  "4. Invalid Auth Value",
			input: map[string][]string{"Authorization": {"abcd 1234"}},
			want: want{
				result: "",
				err:    ErrMalformedAuthHeaderIncluded,
			},
		},
	}

	for _, test := range tests {

		t.Run(test.name, func(t *testing.T) {

			got, err := GetAPIKey(test.input)

			if !errors.Is(err, test.want.err) {
				t.Fatalf("%s: Expected: %v, Got: %v", test.name, test.want.err, err)
			}

			if test.want.err == nil && got != test.want.result {
				t.Fatalf("%s: Expected: %v, Got: %v", test.name, test.want.result, got)
			}

		})

	}

}

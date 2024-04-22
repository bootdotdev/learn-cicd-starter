package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input     http.Header
		want      string
		expectErr error
	}

	tests := []test{
		{input: http.Header{"Authorization": []string{"ApiKey myauth"}}, want: "myauth"},
		{input: http.Header{"Authorization": []string{""}}, want: "", expectErr: ErrNoAuthHeaderIncluded},
		{input: http.Header{}, want: "", expectErr: ErrNoAuthHeaderIncluded},
		{input: http.Header{"Authorization": []string{"malformed"}}, want: "", expectErr: errors.New("malformed authorization header")},
	}

	for _, testCase := range tests {
		got, gotErr := GetAPIKey(testCase.input)
		if testCase.expectErr != nil {
			if gotErr.Error() != testCase.expectErr.Error() {
				t.Errorf("expectErr: %v, got: %v\n", testCase.expectErr, gotErr)
				continue
			}

			continue
		}

		if gotErr != nil {
			t.Errorf("unexpected err: %v\n", gotErr.Error())
			continue
		}

		if got != testCase.want {
			t.Errorf("want: %v, got: %v\n", testCase.want, got)
			continue
		}
	}
}

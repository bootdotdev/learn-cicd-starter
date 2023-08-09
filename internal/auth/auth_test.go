package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetApiKey(t *testing.T) {

	var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")
	var ErrMalformedHeader = errors.New("malformed authorization header")

	type Case struct {
		name      string
		header    http.Header
		want      string
		errorToBe error
	}

	testCases := []Case{
		{
			name: "All Good",
			header: http.Header{
				"Authorization": {"ApiKey abcd"},
			},
			want:      "abcd",
			errorToBe: nil,
		},
		{
			name: "Error Malformed Header",
			header: http.Header{
				"Authorization": {"Key ab"},
			},
			want:      "abcd",
			errorToBe: ErrMalformedHeader,
		},
		{
			name:      "Error No Auth Header",
			header:    http.Header{},
			want:      "abasdf",
			errorToBe: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tc := range testCases {
		got, err := GetAPIKey(tc.header)

		if err != nil {
			if err.Error() != tc.errorToBe.Error() {
				t.Fatalf("%s: expected: %v, got: %v \n", tc.name, tc.errorToBe, err)
			}
		} else if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("expected: %v, got: %v \n", tc.want, got)
		}
	}

}

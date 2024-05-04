package auth

import (
	"errors"
	"net/http"
	"testing"
)

func Test_GetAPIKey(t *testing.T) {
	type m map[string]http.ResponseWriter
	//m := make(map[string]http.ResponseWriter)
	tests := []struct {
		name   string
		input  map[string][]string
		output string
		errr   error
	}{
		{name: "valid Header", input: map[string][]string{"Authorization": {"ApiKey Bearer"}}, output: "Bearer", errr: nil},
		{name: "valid Header", input: map[string][]string{"Authorization": {"ApiKey"}}, output: "", errr: errors.New("malformed authorization header")},
		{name: "valid Header", input: map[string][]string{}, output: "", errr: errors.New("no authorization header included")},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			if err == tc.errr {
				if tc.output != got && err != tc.errr {
					t.Fatalf("%s outputExpected: %v, outputGot: %v, errorExpected: %v, errorGot: ", tc.name, tc.output, tc.errr, err)
				}
			}
		})

	}
}

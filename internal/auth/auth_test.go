package auth

import (
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
		errr   string
	}{
		{name: "valid Header", input: map[string][]string{"Authorization": {"ApiKey Bearer"}}, output: "Bearer", errr: nil},
		{name: "valid Header", input: map[string][]string{"Authorization": {"ApiKey"}}, output: "", errr: "malformed authorization header"},
		{name: "valid Header", input: map[string][]string{}, output: "", errr: "no authorization header "},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			if tc.output != got && err.Error() != tc.errr {
				t.Fatalf("%s outputExpected: %v, outputGot: %v, errorExpected: %v, errorGot: ", tc.name, tc.output, tc.errr, err)
			}
		})

	}
}

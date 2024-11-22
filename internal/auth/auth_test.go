package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		name  string
		input string
		want  string
	}

	tests := map[string]struct {
		input string
		want  string
	}{
		"simple pass": {input: "ApiKey keyplease", want: "keyplease"},
		"no key":      {input: "ApiKey", want: ""},
		"no value":    {input: "", want: ""},
		"no bearer":   {input: " keyplease", want: ""},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			r, err := http.NewRequest("GET", "/test-url", nil)
			if err != nil {
				t.Fatal(err)
			}
			r.Header.Set("Authorization", tc.input)
			got, _ := GetAPIKey(r.Header)
			if !reflect.DeepEqual(tc.want, got) {
				t.Fatalf("%s: expected: %v, got: %v", name, tc.want, got)
			}
		})
	}
}

package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input string
		want  string
	}

	tests := []test{
		{input: "ApiKey keyplease", want: "keyplease"},
		{input: "ApiKey", want: ""},
		{input: "", want: ""},
		{input: " keyplease", want: ""},
	}

	for _, tc := range tests {
		r, err := http.NewRequest("GET", "/test-url", nil)
		if err != nil {
			t.Fatal(err)
		}
		r.Header.Set("Authorization", tc.input)
		got, _ := GetAPIKey(r.Header)
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("expected: %v, got: %v", tc.want, got)
		}
	}
}

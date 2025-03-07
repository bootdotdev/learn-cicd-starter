package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		headerKey  string
		authString string
		want       string
	}

	tests := []test{
		{headerKey: "autho", authString: "", want: ""},
		{headerKey: "autho", authString: "ApiKey abcde", want: ""},
		{headerKey: "Authorization", authString: "", want: ""},
		{headerKey: "Authorization", authString: "ApiKey", want: ""},
		{headerKey: "Authorization", authString: "apikey foo", want: ""},
		{headerKey: "Authorization", authString: "ApiKey foo", want: "foo"},
		{headerKey: "Authorization", authString: "ApiKey foo bar", want: "foo"},
	}

	for i, tc := range tests {
		testHeader := http.Header{}
		testHeader.Set(tc.headerKey, tc.authString)
		res, _ := GetAPIKey(testHeader)
		if tc.want != res {
			t.Fatalf("test %d: expected: '%s', got: '%s'", i+1, tc.want, res)
		}
	}

}

package auth

import (
	"testing"
	"net/http"
)

var tests = []struct{
	name string
	input string
	want string
}{
	{
		name: "proper auth header",
		input: "ApiKey abcdefg",
		want: "abcdefg",
	},
	{
		name: "malformed auth header",
		input: "api key",
		want: "",
	},
	{
		name: "no auth header",
		input: "",
		want: "",
	},
}

func TestAuth(t *testing.T) {
	header := http.Header{}
	for _, ts := range tests {
		t.Run(ts.input, func(t *testing.T) {
			header.Set("Authorization", ts.input)
			out, err := GetAPIKey(header)
			if ts.want != out {
				t.Errorf("[%s] got %q, want %q, error: %s", ts.name, out, ts.want, err)
			}
		})
	}
}

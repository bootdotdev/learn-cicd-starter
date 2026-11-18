package auth

import (
	"net/http"
	"testing"
)

func TestEmpty(t *testing.T) {}

func TestGetAuth(t *testing.T) {

	tests := map[string]struct {
		input string
		want  string
		err   string
	}{
		"simple":       {input: "ApiKey blablabla", want: "blablabla", err: ""},
		"no seperator": {input: "ApiKeyblablabla", want: "", err: "malformed authorization header"},
		"api key":      {input: "ApiKey", want: "", err: "malformed authorization header"},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			header := http.Header{}
			header.Add("Authorization", tc.input)
			got, err := GetAPIKey(header)
			if err != nil {
				if err.Error() != tc.err {
					t.Fatalf("%s: expected: %v, got: %v, err: %v", name, tc.want, got, err)
				}
			}
			if got != tc.want {
				t.Fatalf("%s: expected: %v, got: %v, err: %v", name, tc.want, got, err)
			}
		})
	}
}

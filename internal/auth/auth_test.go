package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  string
	}{
		"shouldSucceed":         {input: http.Header{}, want: "test1"},
		"noToken":               {input: http.Header{}, want: "malformed authorization header1"},
		"noAuthorizationHeader": {input: http.Header{}, want: "no authorization header included"},
	}

	tests["shouldSucceed"].input.Add("Authorization", "ApiKey test1")
	tests["noToken"].input.Add("Authorization", "WrongApiKey test1")

	for name, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if err != nil {
			if err.Error() != tc.want {
				t.Fatalf("%s: expected: %v, got: %v", name, tc.want, err.Error())
			}
			continue
		}
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("%s: expected: %v, got: %v", name, tc.want, got)
		}
	}
}

package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestAuthAPI(t *testing.T) {
	tests := map[string]struct {
		header string
		input  string
		want   string
	}{
		"AuthorizationSucessful": {header: "Authorization", input: "ApiKey key-input", want: "key-input"},
		"AuthorizationFailed":    {header: "WrongHeader", input: "ApiKey key-input", want: ""},
		"ApiKeyNoSpaceFailed":    {header: "WrongHeader", input: "ApiKeykey-input", want: ""},
		"ApiKeyWrongKeyFailed":   {header: "WrongHeader", input: "ApIKey key-input", want: ""},
	}
	for name, tc := range tests {
		testHeader := http.Header{}
		testHeader.Set(tc.header, tc.input)
		key, err := GetAPIKey(testHeader)
		if !reflect.DeepEqual(key, tc.want) {
			t.Fatalf("%s: expect: %v, got: %v", name, tc.want, err.Error())
		}
	}

}

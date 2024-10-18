package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type testInput struct {
		header      string
		headerValue string
		strWant     string
	}

	tests := map[string]testInput{
		"valid":                {header: "Authorization", headerValue: "ApiKey thisismyapikey", strWant: "thisismyapikey"},
		"valid_short":          {header: "Authorization", headerValue: "ApiKey apikey", strWant: "apikey"},
		"invalid":              {header: "Authorization", headerValue: "apple sauce", strWant: ""},
		"invalid_wrong_header": {header: "ApiKey", headerValue: "ApiKey thisismyapikey", strWant: ""},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			header := make(http.Header)
			header.Add(tc.header, tc.headerValue)
			strGot, _ := GetAPIKey(header)
			if !reflect.DeepEqual(tc.strWant, strGot) {
				t.Fatalf("expected: %#v, got: %#v", tc.strWant, strGot)
			}
		})
	}
}

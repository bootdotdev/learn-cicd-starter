package auth

import (
	"errors"
	"net/http"
	"testing"
)

func httpHeader(key, val string) http.Header {
	return http.Header{key: []string{val}}
}

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input      http.Header
		wantString string
		wantError  error
	}{
		"normal":                              {input: httpHeader("Authorization", "ApiKey validAPIKey"), wantString: "validAPIKey", wantError: nil},
		"missing auth header":                 {input: http.Header{}, wantString: "", wantError: ErrNoAuthHeaderIncluded},
		"missing api key":                     {input: httpHeader("Authorization", "ApiKey"), wantString: "", wantError: ErrMalformedAuthHeader},
		"missing api key with trailing space": {input: httpHeader("Authorization", "ApiKey "), wantString: "", wantError: ErrMalformedAuthHeader},
		"malformed auth header val":           {input: httpHeader("Authorization", "APIKey validAPIKey"), wantString: "", wantError: ErrMalformedAuthHeader},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotString, gotError := GetAPIKey(tc.input)
			if gotString != tc.wantString || !errors.Is(gotError, tc.wantError) {
				t.Fatalf("wantString: %v, gotString: %v, wantError: %v, gotError: %v", tc.wantString, gotString, tc.wantError, gotError)
			}
		})
	}
}

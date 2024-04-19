package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		header     http.Header
		wantString string
		wantError  error
	}{
		{header: http.Header{}, wantString: "", wantError: ErrNoAuthHeaderIncluded},
		{header: createAuthHeader("Bearer asdf"), wantString: "", wantError: ErrMalformedAuthHeader},
		{header: createAuthHeader("ApiKey"), wantString: "", wantError: ErrMalformedAuthHeader},
		{header: createAuthHeader("apikey asfd"), wantString: "", wantError: ErrMalformedAuthHeader},
		{header: createAuthHeader("ApiKey asfd"), wantString: "asfd", wantError: nil},
	}

	for _, test := range tests {
		result, err := GetAPIKey(test.header)
		if result != test.wantString {
			t.Errorf("GetAPIKey(%v)=%v, want %v", test.header, result, test.wantString)
		}
		if !errors.Is(err, test.wantError) {
			t.Errorf("GetAPIKey(%v)=%v, want %v", test.header, err, test.wantError)
		}
	}
}

func createAuthHeader(value string) http.Header {
	header := http.Header{}
	header.Add("Authorization", value)
	return header
}

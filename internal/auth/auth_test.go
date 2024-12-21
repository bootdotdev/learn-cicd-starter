package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetApiKeyToSucceed(t *testing.T) {
	cases := []string{"ApiKey asuccessfulapikey", "ApiKey another", "ApiKey t"}

	for _, c := range cases {
		header := http.Header{}
		header.Add("Authorization", c)
		s, err := GetAPIKey(header)
		if err != nil {
			t.Errorf("Error getting api key: %v\n", err)
		}

		if s != strings.TrimPrefix(c, "ApiKey ") {
			t.Errorf("Didn't return the provided api key: got %v, expected: %v\n", s, strings.TrimPrefix(c, "ApiKey "))
		}
	}
}

func TestGetApiKeyShouldFailWhenNoAuthorizationHeader(t *testing.T) {
	header := http.Header{}
	header.Add("Auth", "not a good header")
	_, err := GetAPIKey(header)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("No header provided, expected to fail with error no header. Got : err: %v\n", err)
	}
}

func TestGestApiKeyShouldFailIfMalformed(t *testing.T) {
	cases := []string{"Apikey hdhd", "ApiKey tes tes"}
	header := http.Header{}
	for _, c := range cases {
		header.Add("Authorization", c)
		_, err := GetAPIKey(header)
		if !strings.Contains(err.Error(), "malformed authorization header") {
			t.Errorf("Malformed key provided. Expected to fail with error malformed. Got err: %v\n", err)
		}
	}
}

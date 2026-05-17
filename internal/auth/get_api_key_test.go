package auth

import (
	"net/http"
	"testing"
)

func TestAuthorizationHeaderMissing(t *testing.T) {
	wrongHeaders := http.Header{}
	wrongHeaders.Add("Authentication", "ApiKey super-sercret-key")
	got, err := GetAPIKey(wrongHeaders)

	if got != "" {
		t.Errorf("got: %q, want: %q", got, "")	
	}

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("got error: %v, want: %v", err, ErrNoAuthHeaderIncluded)
	}
}

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey this-is-correct")
	got, _ := GetAPIKey(headers)

	if got != "this-is-correct" {
		t.Errorf("got: %q, want: %q", got, "this-is-correct")
	}

}

func TestMalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "Bearer wrong-token")
	_, err := GetAPIKey(headers)
	if err.Error() != "malformed authorization header" {
		t.Errorf("got error: %v, want: %v", err.Error(), "malformed authorization header")
	}
}

package auth_test

import (
	"fmt"
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetApiKey(t *testing.T) {
	apiKey := "this_is_an_api_key"
	formatted := fmt.Sprintf("ApiKey %s", apiKey)

	{
		header := http.Header{}
		header.Add("Authorization", formatted)

		authkey, err := auth.GetAPIKey(header)
		if err != nil {
			t.Fatalf("successful test returned unexpected err: %v", err)
		}
		if authkey != apiKey {
			t.Fatalf("unexpected result. Expected: `%s` got: `%s`", apiKey, authkey)
		}
	}

	{
		header := http.Header{}
		header.Add("Auth", formatted) // wrong header
		authkey, err := auth.GetAPIKey(header)
		switch {
		case err == nil:
			t.Fatalf("Gave incorrect auth header, received non error value `%s`", authkey)
		case err != auth.ErrNoAuthHeaderIncluded:
			t.Fatalf("Gave incorrect auth header, received incorrect err value `%s`", err)
		}
	}
	{
		header := http.Header{}
		// header.Add("Authorization", formatted) // no header
		authkey, err := auth.GetAPIKey(header)
		switch {
		case err == nil:
			t.Fatalf("Gave incorrect auth header, received non error value `%s`", authkey)
		case err != auth.ErrNoAuthHeaderIncluded:
			t.Fatalf("Gave incorrect auth header, received incorrect err value `%s`", err)
		}
	}
	{
		formatted := fmt.Sprintf("Bearer %s", apiKey) // wrong prfix
		header := http.Header{}
		header.Add("Authorization", formatted) // no header
		authkey, err := auth.GetAPIKey(header)
		if err == nil {
			t.Fatalf("Gave incorrect auth header, received non error value `%s`", authkey)
		}
	}
	{
		formatted := fmt.Sprintf("Bearer%s", apiKey) // malformed
		header := http.Header{}
		header.Add("Authorization", formatted) // no header
		authkey, err := auth.GetAPIKey(header)
		if err == nil {
			t.Fatalf("Gave malformed auth header, received non error value `%s`", authkey)
		}
	}
}

package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestOk(t *testing.T) {
	header := http.Header {}
	header.Add("Authorization", "ApiKey hello")
	if key, err := GetAPIKey(header); err != nil {
		t.Fatal("expected ok, but found error: ", err)
	} else if key != "hello" {
		t.Fatal("expected function to return 'hello', found: ", key)
	}
}

func TestWrongApiKey(t *testing.T) {
	header := http.Header {}
	header.Add("Authorization", "WrongApiKey hello")
	if key, err := GetAPIKey(header); err.Error() != "malformed authorization header" {
		t.Fatal("expected malformed authorization header, found: ", err)
	} else if key != "" {
		t.Fatal("expected key to be empty, found: ", key)
	}
}

func TestNoAuthHeader(t *testing.T) {
	header := http.Header {}
	if key, err := GetAPIKey(header); !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Fatal("expected ErrNoAuthHeaderIncluded, found: ", err)
	} else if key != "" {
		t.Fatal("expected key to be empty, found: ", key)
	}
}

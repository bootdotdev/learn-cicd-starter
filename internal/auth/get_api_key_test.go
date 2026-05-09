package auth

import (
	"log"
	"net/http"
	"testing"
)

func TestGetAPIKeyHappyPath(t *testing.T) {
	req, err := http.NewRequest("GET", "http://example.com", nil)
	if err != nil {
		log.Fatal(err)
	}
	token := "ApiKey abc123"
	req.Header.Set("Authorization", token)
	got, err := GetAPIKey(req.Header)
	if err != nil {
		log.Fatal(err)
	}
	want := "abc123"
	if got != want {
		t.Errorf("expected: %v, got: %v", want, got)
	}
}

func TestGetAPIKeyMalformed(t *testing.T) {
	req, err := http.NewRequest("GET", "http://example.com", nil)
	if err != nil {
		log.Fatal(err)
	}
	token := "Bearer abc123"
	req.Header.Set("Authorization", token)
	_, err = GetAPIKey(req.Header)
	if err != nil {
		t.Errorf("\nAuthorization header should only this format:\n'ApiKey <token>'\nbut it accepted:\n'%v'", token)
	}
}

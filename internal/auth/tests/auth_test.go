package tests

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestAuthWithValidHeaders(t *testing.T) {
	keys := []string{
		"ApiKey 123",
		"ApiKey abc",
		"ApiKey ZZZHDAWHDASDRE",
	}

	expected := []string{
		"123",
		"abc",
		"ZZZHDAWHDASDRE",
	}

	for i := range keys {
		headers := http.Header{}
		headers.Add("Authorization", keys[i])

		key, err := auth.GetAPIKey(headers)

		if err != nil {
			t.Fatalf("An error occured while generating API key: %v", err)
		}

		if key != expected[i] {
			t.Fatalf("An error occured while generating API key. Expected %v, got %v", expected[i], key)
		}
	}
}

func TestAuthWitnInvalidHeaders(t *testing.T) {
	keys := []string{
		"Bearer 123",
		"Choco 3333",
		"Hi asdfg",
	}

	for i := range keys {
		headers := http.Header{}
		headers.Add("Authorization", keys[i])
		if _, err := auth.GetAPIKey(headers); err == nil {
			t.Fatal("Expected error while generating API key. Got nil")
		}
	}
}

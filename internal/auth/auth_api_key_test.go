package auth

import (
	"net/http"
	"testing"
)

func TestAuth(t *testing.T) {
	testHeader := http.Header{}

	testHeader["Authorization"] = []string{"kunal"}
	got, err := GetAPIKey(testHeader)
	if err != nil {
		return
	}

	want := "malformed authorization header"

	if got != want {
		t.Fatalf("malformed authorization header")
	}
}

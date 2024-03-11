package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{}
	header.Add("Authorization", "ApiKey authtoken")

	expected := "authtoken"
	key, err := GetAPIKey(header)
	if err != nil {
		t.Fatalf("expected: %v, got: %v", expected, key)
	}

	got := key
	if expected != got {
		t.Fatalf("expected: %v, got: %v", expected, key)
	}

}

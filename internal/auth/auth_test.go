package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyWorks(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey abcd")
	got, err := GetAPIKey(header)
	want := "abcd"
	if err != nil {
		t.Fatalf("Not expecting err: %v", err)
	}
	if got != want {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

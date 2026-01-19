package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 1234567890")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	want := "1234567890"
	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

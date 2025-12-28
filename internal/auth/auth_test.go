package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{}

	header.Set("Authorization", "ApiKey sometext")
	res, _ := GetAPIKey(header)
	if res == "sometext" {
		t.Errorf("expected sometext, got %s", res)
	}
}

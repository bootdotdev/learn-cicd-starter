package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	apiKey := "ApiKey this_is_a_temporary_api_key"
	expect := "this_is_a_temporary_api_key"
	header := make(http.Header)
	header.Set("Authorization", apiKey)

	res, err := GetAPIKey(header)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if res != expect {
		t.Errorf("expected %q, got %q", expect, res)
	}
}

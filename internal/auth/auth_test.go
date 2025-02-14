package auth

import (
	"net/http"
	"testing"
)

func TestGetAPI(t *testing.T) {
	header1 := http.Header{}
	apikey := "my-random-apikey"
	header1.Set("Authorization", "ApiKey my-random-apikey")
	result, err := GetAPIKey(header1)
	if err != nil {
		t.Fatal("error with", err)
	}
	if result != "my-random-apikey" {
		t.Fatalf("expected: %v, got: %v", apikey, result)
	}

	header2 := http.Header{}
	header2.Set("Authorization", "Bearer my-random-token")
	_, err = GetAPIKey(header2)
	if err == nil {
		t.Fatal("Expect error of non ApiKey, got nil")
	}

	header3 := http.Header{}
	header3.Set("Authorization", "ApiKey")
	_, err = GetAPIKey(header3)
	if err == nil {
		t.Fatal("Expect error of malformed ApiKey, got nil")
	}
}

package auth

import (
	"testing"
	"net/http"
)

func TestGetApiKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey test-key")

	got, err := GetAPIKey(headers)
	if err != nil{
		t.Fatalf("GetApiKey() error =%v", err)
	}
	if got != "test-key" {
		t.Errorf("GetApiKey() = %q, want %q", got, "test-key")
	}
}
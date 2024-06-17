package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetApiKey(t *testing.T) {
	r := httptest.NewRequest(http.MethodGet, "/", nil)
	r.Header.Add("Authorization", "ApiKey 1234")
	key, err := auth.GetAPIKey(r.Header)
	if key != "1234" {
		t.Errorf("Expected 1234, got %s", key)
	}
	if err != nil {
		t.Errorf("Expected no error, got %s", err)
	}
}

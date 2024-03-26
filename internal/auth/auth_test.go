package auth

import (
	"net/http"
	"testing"
)

func TestBearer(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}
	apiKeyExpected := "sandro"
	req.Header.Set("Authorization", "Bearer "+apiKeyExpected)

	apiKey, err := GetAPIKey(req.Header)
	if err == nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if apiKey == apiKeyExpected {
		t.Error("This should not return the request apikey")
	}
}

func TestCorrect(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}
	apiKeyExpected := "sandro"
	req.Header.Set("Authorization", "ApiKey "+apiKeyExpected)

	apiKey, err := GetAPIKey(req.Header)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if apiKey != apiKeyExpected {
		t.Errorf("Expected no error, got %v", err)
	}
}

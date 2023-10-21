package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyValid(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("fail to create request: %s", err.Error())
	}
	req.Header.Set("Authorization", "ApiKey ValidToken")

	_, err = GetAPIKey(req.Header)
	if err != nil {
		t.Errorf("valid token reutrned error: %v", err)
	}
}

func TestGetAPIKeyMissingPrefix(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("fail to create request: %s", err.Error())
	}
	req.Header.Set("Authorization", "ValidToken")

	_, err = GetAPIKey(req.Header)
	if err.Error() != "malformed authorization header" {
		t.Errorf("expected malformed authorization header, got: %v", err)
	}
}

func TestGetAPIKeyMissingToken(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("fail to create request: %s", err.Error())
	}
	req.Header.Set("Authorization", "ApiKey")

	_, err = GetAPIKey(req.Header)
	if err.Error() != "malformed authorization header" {
		t.Errorf("expected malformed authorization header, got: %v", err)
	}
}

func TestGetAPIKeyEmptyAuthorization(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("fail to create request: %s", err.Error())
	}
	req.Header.Set("Authorization", "")

	_, err = GetAPIKey(req.Header)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected %v, got: %v", ErrNoAuthHeaderIncluded.Error(), err)
	}
}

func TestGetAPIKeyMissingAuthorization(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("fail to create request: %s", err.Error())
	}

	_, err = GetAPIKey(req.Header)
	if err == ErrNoAuthHeaderIncluded {
		t.Errorf("expected %v, got: %v", ErrNoAuthHeaderIncluded.Error(), err)
	}
}

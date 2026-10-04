package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_RequiresAuthorizationHeader(t *testing.T) {
	_, err := GetAPIKey(http.Header{})
	if err == nil {
		t.Errorf("expected err to not be nil")
	}
}

func TestGetAPIKey_RequiresWelformedAuthorizationHeader(t *testing.T) {
	_, err := GetAPIKey(http.Header{"Authorization": []string{"ApiKey"}})
	if err == nil {
		t.Errorf("expected err to not be nil")
	}

	_, err = GetAPIKey(http.Header{"Authorization": []string{"ApiKey 123456"}})
	if err != nil {
		t.Errorf("expected err to not be nil")
	}
}

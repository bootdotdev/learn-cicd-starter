package auth

import (
	"net/http/httptest"
	"testing"
)

var testReq = httptest.NewRequest("GET", "/api", nil)

func TestGetAPIKeyGoodAuth(t *testing.T) {
	testReq.Header.Set("Authorization", "ApiKey 42069")
	want := "42069"
	got, err := GetAPIKey(testReq.Header)
	if err != nil {
		t.Errorf("GetAPIKey() returned an error: %v", err)
	}
	if got != want {
		t.Errorf("GetAPIKey() = %v, want %v", got, want)
	}
}

func TestGetAPIKeyBadAuth(t *testing.T) {
	testReq.Header.Set("Authorization", "Bearer 42069")
	got, err := GetAPIKey(testReq.Header)
	if err == nil {
		t.Errorf("GetAPIKey() did not return an error; got %v", got)
	}
}

func TestGetAPIKeyNoAuth(t *testing.T) {
	got, err := GetAPIKey(testReq.Header)
	if err == nil {
		t.Errorf("GetAPIKey() did not flag missing header as expected; got %v", got)
	}
}

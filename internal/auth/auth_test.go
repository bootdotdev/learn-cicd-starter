package auth

import (
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "ApiKey secret")
	got, _ := GetAPIKey(req.Header)
	want := "secret"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

func TestGetAPIKeyEmpty(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	got, err := GetAPIKey(req.Header)
	if err == nil || got != "" {
		t.Fatalf("expected: a error and empty value, got: %v", got)
	}
}

func TestGetAPIKeyMalformed_1(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "ApiKey")
	got, err := GetAPIKey(req.Header)
	if err == nil || got != "" {
		t.Fatalf("expected: a error and empty value, got: %v", got)
	}
}

func TestGetAPIKeyMalformed_2(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "Malformation secret")
	got, err := GetAPIKey(req.Header)
	if err == nil || got != "" {
		t.Fatalf("expected: a error and empty value, got: %v", got)
	}
}

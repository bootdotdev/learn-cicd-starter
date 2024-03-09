package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestHandlerReadiness(t *testing.T) {
	req, err := http.NewRequest("GET", "http://localhost:8080/v1/healthz", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handlerReadiness)

	handler.ServeHTTP(rr, req)
	if rr.Code != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", rr.Code, http.StatusOK)
	}
}

func TestGetAPIKey(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}
	want := "2474024740247402"
	req.Header.Set("Authorization", "ApiKey "+want)
	got, err := auth.GetAPIKey(req.Header)
	if err != nil {
		t.Fatal(err)
	}
	if got != want {
		t.Errorf("function returns wrong value for apikey: got %s want %s", got, want)
	}
}

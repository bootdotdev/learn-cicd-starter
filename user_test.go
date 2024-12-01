package main

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestBurgers(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey BEANSBEANSBEANS")
	output, err := auth.GetAPIKey(header)
	if err != nil {
		t.Fatalf("Error thrown: %s", err)
	}
	expected := "BEANSBEANSBEANS"
	if output != expected {
		t.Fatalf("Expected: %v, got: %v", expected, output)
	}
}

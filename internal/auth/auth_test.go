package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{
		"Authorization": []string{"ApiKey nabinkhanal"},
	}
	result, err := GetAPIKey(header)
	if err != nil {
		t.Fatal("Error is not nil")
	}
	if result != "nabinkhanal" {
		t.Fatal("the value is not correct")
	}
}

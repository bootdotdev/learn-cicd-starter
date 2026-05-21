package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey 12345")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("error inesperado: %v", err)
	}
	if key != "12345" {
		t.Fatalf("se esperaba '12345', se obtuvo: %v", key)
	}
}

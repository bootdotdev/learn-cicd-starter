package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 123456")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("esperava nil erro, recebeu: %v", err)
	}
	if key != "123456" {
		t.Errorf("esperava chave 123456, recebeu: %v", key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("esperava erro por ausência do header Authorization")
	}
}

package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testKey := "my-api-key"

	headers := http.Header{
		"Authorization": []string{fmt.Sprintf("ApiKey %s", testKey)},
	}

	key, err := GetAPIKey(headers)

	if err != nil {
		t.Error("GetAPIKey threw an error")
	}

	if key != testKey+"fail" {
		t.Errorf(`Expected %s, got %s`, testKey, key)
	}
}

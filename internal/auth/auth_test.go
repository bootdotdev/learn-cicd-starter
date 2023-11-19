package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	key := "some-api-key"
	request := http.Request{
		Header: http.Header{},
	}
	request.Header.Add("Authorization", "ApiKey "+key)

	actual, err := GetAPIKey(request.Header)
	if err != nil {
		t.Errorf("Expected no error, got: %v", err)
	}

	if actual != key {
		t.Errorf("Expected %v, got %v", key, actual)
	}
}

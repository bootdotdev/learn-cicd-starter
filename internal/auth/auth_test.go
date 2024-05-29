package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	h := http.Header{}
	h.Add("Authorization", "testing")
	key, err := GetAPIKey(h)
	if err == nil {
		t.Error("should be error")
	}
	if len(key) != 0 {
		t.Error("should return empty string")
	}
}

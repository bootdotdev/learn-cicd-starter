package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	testHeaders := http.Header{}
	testHeaders.Set("Authorization", "ApiKey 1234")

	key, err := GetAPIKey(testHeaders)
	if err != nil {
		t.Errorf("GetAPIKey() error = %v", err)
		return
	}
	if key != "1234" {
		t.Errorf("GetAPIKey() = %v, want %v", key, "1234")
		return
	}
}

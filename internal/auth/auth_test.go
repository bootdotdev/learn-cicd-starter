package auth

import (
	"net/http"
	"testing"
)

func TestCorrectAPIKey(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	req.Header.Set("Authorization", "ApiKey zesxrctfvygbunijmo78516zesxdfjnimkop")

	actual_key, err := GetAPIKey(req.Header)
	if actual_key != "zesxrctfvygbunijmo78516zesxdfjnimkop" || err != nil {
		t.Errorf("incorrect or missing key")
	}
}

func TestMissingHeader(t *testing.T) {
	req, _ := http.NewRequest("GET", "/", nil)
	actual_key, err := GetAPIKey(req.Header)
	if actual_key != "" || err == nil {
		t.Errorf("expected empty key and an error when header is missing, got key=%q, err=%v", actual_key, err)
	}
}

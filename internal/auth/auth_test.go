package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	apiKey := "lolimnotakeyluls"
	fake_header := http.Header{
		"Authorization": []string{"ApiKey " + apiKey},
	}

	got, err := GetAPIKey(fake_header)
	if err != nil {
		t.Fatal(err.Error())
	}
	if got != apiKey {
		t.Fatal("das not my apikey fools")
	}
}

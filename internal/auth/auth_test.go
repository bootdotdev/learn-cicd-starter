package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGoodApiKey(t *testing.T) {
	authorizationHeader := "ApiKe jasfkjash812m3b!418h41"
	expectedKey := "jasfkjash812m3b!418h41"

	req, err := http.NewRequest("", "", nil)

	if err != nil {
		t.Errorf("Could not create request")
		return
	}

	req.Header.Add("Authorization", authorizationHeader)

	apiKey, err := GetAPIKey(req.Header)

	if err != nil {
		fmt.Println(err.Error())
		t.Errorf("Error getting api key")
		return
	}

	if apiKey != expectedKey {
		t.Errorf("Unexpected api key.")
		return
	}

}

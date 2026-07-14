package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGETApiKey(t *testing.T) {
	manualAuth := "thisIsAuthHeader"
	customHeader := http.Header{
		"Authorization": []string{
			"ApiKey thisIsAuthHeader",
		},
	}
	//customHeader.Add("Authorization", "ApiKey thisIsAuthHeader")
	got, err := GetAPIKey(customHeader)
	if err != nil {
		fmt.Printf("lol%v", err)
	}
	if manualAuth != got || err != nil {
		t.Fatalf("expected: %v, got: %v", manualAuth, got)
	}
}

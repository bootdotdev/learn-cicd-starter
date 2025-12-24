package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	normalHeader := http.Header{}
	normalHeader.Add("Authorization", "ApiKey dummykey123")

	_, err := GetAPIKey(normalHeader)
	if err != nil {
		t.Errorf("error with correct formatting")
	}

	missingHeader := http.Header{}

	_, err = GetAPIKey(missingHeader)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("missing auth header error not working")
	}

	deformedHeader := http.Header{}
	deformedHeader.Add("Authorization", "Lol. Lmao.")

	_, err = GetAPIKey(deformedHeader)
	if err == nil {
		t.Errorf("deformed header error not working")
	}
}

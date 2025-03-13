package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_InvalidKeyEmptyAuth(t *testing.T) {
	var input http.Header = http.Header{}
	input.Set("Authorization", "")

	output, err := GetAPIKey(input)
	if output == "" && err != ErrNoAuthHeaderIncluded {
		t.Fatalf("Blank Authorization Key should return \"\" but recieved \"%v\" instead.\n\tErr: %v",
			output, err)
	}
}

func TestGetAPIKey_InvalidKeyWithSpace(t *testing.T) {
	var input http.Header = http.Header{}
	input.Set("Authorization", "Test1 Test2")

	output, err := GetAPIKey(input)
	if output == "" && err.Error() != "malformed authorization header" {
		t.Fatalf("Should not be able to process multiple values in Authorization. Recieved: \"%v\" \n\tErr: %v",
			output, err)
	}
}

func TestGetAPIKey_ValidKey(t *testing.T) {
	var input http.Header = http.Header{}
	input.Set("Authorization", "Test1")

	output, err := GetAPIKey(input)
	if output != "Test1" && err != nil {
		t.Fatalf("Should not recieve error when attempting to get valid APIKey. Recieved: \"%v\" \n\tErr: %v",
			output, err)
	}
}

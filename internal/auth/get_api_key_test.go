package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// TEST 1: The "Success" Case
	// We create a header with a valid ApiKey
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey 12345")

	got, _ := GetAPIKey(headers)
	want := "this test will fail"

	if got != want {
		t.Errorf("expected %v, got %v", want, got)
	}

	// TEST 2: The "Missing Header" Case
	// We create an empty header to see if it catches the error
	emptyHeaders := http.Header{}
	_, err := GetAPIKey(emptyHeaders)

	if err == nil {
		t.Errorf("expected an error but didn't get one")
	}
}

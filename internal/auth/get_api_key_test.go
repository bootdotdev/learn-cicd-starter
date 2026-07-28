package auth

import (
	"net/http"
	"testing"
)

func TestGetApi(t *testing.T) {
	headers := make(http.Header)
	headers.Set("Authorization", "b a")
	actual, err := GetAPIKey(headers)
	expected := "b a"

	if err != nil || string(actual) == expected {
		t.Fatalf("expected '%s' got '%s'", expected, actual)
	}

}

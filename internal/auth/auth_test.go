package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{
		"Authorization": {"ApiKey 1234567"},
		"Content-Type":  {"application/json"},
	}

	got, err := GetAPIKey(headers)
	want := "1234567"
	if err != nil {
		t.Errorf("Failed to get API with the following error: %v", err)
	}
	fmt.Println("GetAPIKey returned: ", got)

	fmt.Println("Wanted: ", want)

	if got != want {
		t.Errorf("Fetched data is not as expected. Got '%s', Want '%s'", got, want)
	}
}

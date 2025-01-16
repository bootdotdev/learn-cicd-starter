package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestApiKey(t *testing.T) {
	want := "testapikey"

	var headers http.Header = make(map[string][]string)
	headers.Add("Authorization", fmt.Sprintf("ApiKey %s", want))

	got, _ := GetAPIKey(headers)
	if want != got {
		t.Fatalf("expected %v, got: %v", want, got)
	}
}

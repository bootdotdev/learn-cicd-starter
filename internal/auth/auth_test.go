package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestAuth(t *testing.T) {
	req, err := http.NewRequest("GET", "http://localhost:8080", nil)
	req.Header.Set("Authorization", "ApiKey apiKey")
	got, error := GetAPIKey(req.Header)
	want := "apiKey"
	if !reflect.DeepEqual(want, got) || err != nil || error != nil {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

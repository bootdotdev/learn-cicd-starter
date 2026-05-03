package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 12345")

	got, _ := GetAPIKey(headers)
	want := "12345"

	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

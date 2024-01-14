package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := make(http.Header)
	header.Add("Authorization", "ApiKey 1q234e1234")
	got, _ := GetAPIKey(header)
	want := "1q234e1234"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

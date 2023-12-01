package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := make(http.Header)
	headers.Set("Authorization", "ApiKey 1234")
	got, err := GetAPIKey(headers)
	want := "1234"
	if err != nil {
		t.Errorf("expected: %v, got %v", want, err)
	}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("expected: %v, got %v", want, got)
	}
}

package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey_Valid(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")
	got, err := GetAPIKey(headers)
	want := "my-secret-key"
	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %q, want %q, err %v", got, want, err)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}
	got, err := GetAPIKey(headers)
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("expected error %v, got %v, key %q", ErrNoAuthHeaderIncluded, err, got)
	}
}

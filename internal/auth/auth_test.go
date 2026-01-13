package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestEmptyGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "")
	got, err := GetAPIKey(headers)
	want := ""
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("%v\nexpected: %v, got: %v", err, want, got)
	}
}

func TestValidGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey some-secret-key")
	got, err := GetAPIKey(headers)
	want := "some-secret-key"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("%v\nexpected: %v, got: %v", err, want, got)
	}
}

func TestInvalidGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Add("Classification", "Private Stuff")
	got, err := GetAPIKey(headers)
	want := ""
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("%v\nexpected: %v, got: %v", err, want, got)
	}
}

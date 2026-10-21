package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{
		"Authorization": {"ApiKey testing"},
	}
	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatal(err)
	}
	want := "testing"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}

}

func TestGetAPIKeyMissingHeader(t *testing.T) {
	headers := http.Header{
		"Authorization": {"ApiKey"},
	}
	got, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("Expected Error, but got none")
	}
	want := ""
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got %v", want, got)
	}
}

func TestGetAPIKeyMalformed(t *testing.T) {
	headers := http.Header{
		"Authorization": {"ApiKy wwwaaa"},
	}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("Error expected, but got none")
	}
	want := "malformed authorization header"
	if !reflect.DeepEqual(want, err.Error()) {
		t.Fatalf("expected: %v, got: %v", want, err)
	}
}

package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKeyErrors(t *testing.T) {
	_, err := GetAPIKey(http.Header{
		"Authorization": {"Basic foo"},
	})
	if err == nil {
		t.Fatalf("Expected an error, but error was nil")
	}
}

func TestGetAPIKeyWorks(t *testing.T) {
	got, err := GetAPIKey(http.Header{
		"Authorization": {"ApiKey 123"},
	})
	if err != nil {
		t.Fatalf("Error should be nil but it wasn't")
	}
	want := "123"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("got %#v, want %#v", got, want)
	}

}

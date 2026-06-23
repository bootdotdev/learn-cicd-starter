package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	got, _ := GetAPIKey(http.Header{
		"Authorization": []string{"ApiKey test"}})
	want := "test"
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v, want %v", got, want)
	}

}

package auth

import (
	"testing"
	"reflect"
	"net/http"
)

func TestGetAPIKey(t *testing.T) {
	got, _ := GetAPIKey(http.Header{
		"Authorization": []string{"ApiKey test"},})
	want := "test"
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v, want %v", got, want)
	}

}

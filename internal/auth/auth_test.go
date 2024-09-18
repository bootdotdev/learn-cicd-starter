package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetApi(t *testing.T) {
	var header http.Header
	got, _ := GetAPIKey(header)
	want := "craiso nakin"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

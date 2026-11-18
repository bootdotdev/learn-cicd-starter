package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	header := http.Header{
		"Authorization": []string{"ApiKey my-secret-key"},
	} 
	got, _ := GetAPIKey(header)
	want := "my-secret-key"
	if !reflect.DeepEqual(want, got){
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}
func TestGetAPIKey_NoHeader(t *testing.T) {
	header := http.Header{}
	_, err := GetAPIKey(header)
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected: %v, got: %v", ErrNoAuthHeaderIncluded, err)
	}
}
func TestGetAPIKey_MalformedHeader(t *testing.T) {
	header := http.Header{
		"Authorization": []string{"Bearer my-secret-key"},
	} 
	_, err := GetAPIKey(header)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Fatalf("expected: %v, got: %v", "malformed authorization header", err)
	}
}
package auth

import (
	"reflect"
	"testing"
	"net/http"
	"errors"

)

func TestGetAPIKey(t *testing.T){
	testHeader := http.Header{}
	testHeader.Set("Authorization","ApiKey 123456")

	got,_ := GetAPIKey(testHeader)
	want := "123456"
	if !reflect.DeepEqual(want,got){
		t.Fatalf("expected: %v, got: %v", want, got)
	}


}

func TestGetApiKeyNoAuthHeader(t *testing.T){
	testHeader := http.Header{}
	_,err := GetAPIKey(testHeader)
	want := ErrNoAuthHeaderIncluded
	if !errors.Is(want,err){
		t.Fatalf("expected: %v, got: %v", want, err)
	}
}

func TestGetApiKeyBadAuth(t *testing.T){
	testHeader := http.Header{}
	testHeader.Set("Authorization","123456")
	_,err := GetAPIKey(testHeader)
	want := "malformed authorization header"
	if err.Error() != want{
		t.Fatalf("expected: %v, got: %v", want, err)
	}
}

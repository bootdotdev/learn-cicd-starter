package auth

import (
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	request := httptest.NewRequest("GET", "http://localhost:8000", nil)
	request.Header = http.Header{
		"Host": {"localhost"},
    "Content-Type": {"application/json"},
		"Authorization": {"ApiKey thisIsAnAPIKey"},
	}

	got, _ := GetAPIKey(request.Header)

	want := "thisIsAnAPIKey"

	if  !reflect.DeepEqual(want, got){
		t.Fatalf("expected: %v, got: %v\n", want, got)
	}
	
}
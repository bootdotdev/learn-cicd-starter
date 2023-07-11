package auth

import (
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	mockReq := httptest.NewRequest("GET", "http://localhost:8000", nil)
	mockReq.Header = http.Header{
		"Host": {"localhost"},
    "Content-Type": {"application/json"},
		"Authorization": {"ApiKey thisIsAnAPIKey"},
	}

	got, err := GetAPIKey(mockReq.Header)
	if err != nil {
		got = err.Error()
	}

	want := "thisIsAnAPIKey"

	if  !reflect.DeepEqual(want, got){
		t.Fatalf("expected: %v, got: %v\n", want, got)
	}
	
}
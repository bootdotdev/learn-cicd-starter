package auth

import (
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "ApiKey secret")
	got, _ := GetAPIKey(req.Header)
	want := "secret"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

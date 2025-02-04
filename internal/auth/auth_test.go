package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestAuthNull(t *testing.T) {
	testHeader := http.Header{}
	_, goterr := GetAPIKey(testHeader)
	_, wanterr := "", ErrNoAuthHeaderIncluded
	if !reflect.DeepEqual(wanterr, goterr) {
		t.Fatalf("expected: %v, got: %v", wanterr, goterr)
	}
}

func TestAuthBadAuth(t *testing.T) {
	testHeader := http.Header{
		"Authorization": []string{"yoyoyo"},
	}
	_, goterr := GetAPIKey(testHeader)
	wanterrstr := "malformed authorization header"
	if !reflect.DeepEqual(wanterrstr, goterr.Error()) {
		t.Fatalf("expected: %v, got: %v", wanterrstr, goterr)
	}

}

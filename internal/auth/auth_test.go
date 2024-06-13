package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestAuth(t *testing.T) {
	bearerToken := "ey.123FADolo1233"
	header := http.Header{}
	header.Set("Authorization", "ApiKey "+bearerToken)
	got, _ := GetAPIKey(header)
	want := bearerToken
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

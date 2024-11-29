package auth

import (
	"net/http"
	// "net/http/httptest"
	"reflect"
	"testing"
)

var headers http.Header = http.Header{
	"Authorization": []string{"ApiKey blabla"},
}

func TestGetAPIKey(t *testing.T) {

	// headers.Set("Authorization", "Bearer blabla-secret-apikey")

	gotValue, gotError := GetAPIKey(headers)
	wantValue := "blabla"
	if gotError != nil {
		// fail test?
	}
	if !reflect.DeepEqual(gotValue, wantValue) {
		t.Fatalf("expected: %v, got: %v", wantValue, gotValue)
	}
}

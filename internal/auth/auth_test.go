package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	input := make(http.Header)
	input.Set("Authorization", "ApiKey MyApiKey")

	got, err := GetAPIKey(input)
	if err != nil {
		t.Fatal("GetAPIKey return an error: ", err)
	}

	want := "MyApiKey"
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

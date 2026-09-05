package auth

import (
	"reflect"
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey your-api-key-here")
	got, err := GetAPIKey(header)

	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	want := "your-api-key-here"

	if !reflect.DeepEqual(want, got) {
		t.Fatalf("expected %q, got: %q",want, got)
	}

}



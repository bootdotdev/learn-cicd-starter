package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetApiKeyValidValue(t *testing.T) {
	const want = "value"
	header := http.Header{}
	header.Set("Authorization", "ApiKey " + want)
	got, err := GetAPIKey(header);
	if err != nil {
		t.Fatalf("expected: %v, got: %s", want, err.Error())
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("expected: %v, got: %v", want, got)
	}
}

func TestGetApiKeyNoAuthHeader(t *testing.T) {
	header := http.Header{}
	_, err := GetAPIKey(header);
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected: %v, got: %s", ErrNoAuthHeaderIncluded, err.Error())
	}
}

func TestGetApiKeyInvalidValue(t *testing.T) {
	const want = "value"
	header := http.Header{}
	header.Set("Authorization", want)
	_, err := GetAPIKey(header);
	if err == nil {
		t.Fatal("Expected error, but none happened")
	} else if err.Error() != "malformed authorization header" {
		t.Fatalf("expected: %v, got: %s", want, err.Error())
	}	
}

package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	headers := http.Header{}

	str, err := GetAPIKey(headers)

	if str != "" {
		t.Fatalf("expected: %s, got: %s", "", str)
	}

	want := ErrNoAuthHeaderIncluded
	if want != err {
		t.Fatalf("expected: %v, got: %v", want, err)
	}
}

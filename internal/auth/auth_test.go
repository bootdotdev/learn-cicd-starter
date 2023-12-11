package auth

import (
	"net/http"
	"testing"
)

func TestFail(t *testing.T) {
    h := http.Header{}
    h.Add("Authorization", "")
    _, err := GetAPIKey(h)
    if err == ErrNoAuthHeaderIncluded{
        t.Fatalf("expected: %v, got: %v", ErrNoAuthHeaderIncluded, err)
    }
}

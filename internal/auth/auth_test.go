package auth

import (
  "testing"
  "net/http"
)

func TestThing(t *testing.T) {
  if 1 == 1 {
    t.Fatalf("Oh no oh me oh my numbers")
  }
}

func TestEmptyAuthHeader(t *testing.T) {
  var header http.Header = make(map[string][]string)
  _, err := GetAPIKey(header)
  s := err.Error()
  if s != "no authorization header included" {
    t.Fatalf("Unexpected error: %v", s)
  }
}


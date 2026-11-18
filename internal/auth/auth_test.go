package auth

import (
 "net/http"
 "testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
 h := http.Header{}
 h.Set("Authorization", "ApiKey 12345")

 key, err := GetAPIKey(h)
 if err != nil {
  t.Fatalf("expected no error, got %v", err)
 }
 if key != "12345" {
  t.Errorf("expected key '12345', got '%s'", key)
 }
}

func TestGetAPIKey_MissingPrefix(t *testing.T) {
 h := http.Header{}
 h.Set("Authorization", "12345")

 _, err := GetAPIKey(h)
 if err == nil {
  t.Fatal("expected an error, got nil")
 }
}

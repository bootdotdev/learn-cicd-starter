package auth

import "testing"

func TestGetAPIKey(t *testing.T) {
    key := GetAPIKey("Authorization: ApiKey 12345")
    expected := "12345"

    if key != expected {
        t.Errorf("Expected %s but got %s", expected, key)
    }
}


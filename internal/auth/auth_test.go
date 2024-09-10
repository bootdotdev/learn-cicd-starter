package auth

import (
    "testing"
    "net/http"
)

func TestGetAPIKey(t *testing.T) {
    testHeaders := http.Header{}
    testHeaders.Add("Authorization", "ApiKey 123456")
    result, err := GetAPIKey(testHeaders)
    if err != nil {
        t.Errorf("failed getting API key: %s", err)
    }
    if result != "123456" {
        t.Errorf("want 123456, got %s", result)
    }
}

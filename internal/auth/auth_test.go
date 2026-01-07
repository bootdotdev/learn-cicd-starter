package auth

import (
    "net/http"
    "testing"
)

func TestGetAPIKey(t *testing.T) {
    t.Run("returns API key when header is valid", func(t *testing.T) {
        headers := http.Header{}
        headers.Set("Authorization", "ApiKey test123")
        
        key, err := GetAPIKey(headers)
        
        if err != nil {
            t.Errorf("Expected no error, got %v", err)
        }
        if key != "test123" {
            t.Errorf("Expected 'test123', got %s", key)
        }
    })
    
    t.Run("returns error when no authorization header", func(t *testing.T) {
        headers := http.Header{}
        
        key, err := GetAPIKey(headers)
        
        if err == nil {
            t.Error("Expected error, got nil")
        }
        if err != ErrNoAuthHeaderIncluded {
            t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
        }
        if key != "" {
            t.Errorf("Expected empty key, got %s", key)
        }
    })
    
    // This will FAIL on purpose
    t.Run("forced failure", func(t *testing.T) {
        t.Error("Breaking CI on purpose")
    })
}

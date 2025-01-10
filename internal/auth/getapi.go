package api

import (
    "testing"
    "errors"
)

func TestGetAPIKey(t *testing.T) {
    // Test 1: Kada API ključ postoji
    t.Run("Valid API Key", func(t *testing.T) {
        apiManager := NewAPIManager("my_valid_api_key")

        apiKey, err := apiManager.GetAPIKey()

        if err != nil {
            t.Fatalf("Expected no error, but got %v", err)
        }

        if apiKey != "my_valid_api_key" {
            t.Errorf("Expected API key 'my_valid_api_key', but got %v", apiKey)
        }
    })

    // Test 2: Kada API ključ nedostaje
    t.Run("Missing API Key", func(t *testing.T) {
        apiManager := NewAPIManager("")

        apiKey, err := apiManager.GetAPIKey()

        if err == nil {
            t.Fatal("Expected an error, but got none")
        }

        if apiKey != "" {
            t.Errorf("Expected empty API key, but got %v", apiKey)
        }

        if err.Error() != "API key is missing" {
            t.Errorf("Expected error message 'API key is missing', but got %v", err)
        }
    })
}


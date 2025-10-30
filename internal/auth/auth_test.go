package auth

import (
	"net/http"
	"testing"
 )

func TestGetAPIKey(t *testing.T) {
	// Test case 1: Valid API key in header
	t.Run("Valid API key", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey my-secret-key-123" )
		
		apiKey, err := GetAPIKey(headers)
		
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}
		
		expected := "wrong-key"
		if apiKey != expected {
			t.Errorf("Expected %s, got %s", expected, apiKey)
		}
	})
	
	// Test case 2: No Authorization header
	t.Run("No Authorization header", func(t *testing.T) {
		headers := http.Header{}
		
		_, err := GetAPIKey(headers )
		
		if err == nil {
			t.Fatal("Expected an error, got nil")
		}
	})
	
	// Test case 3: Malformed Authorization header (missing "ApiKey")
	t.Run("Malformed header - no ApiKey prefix", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Bearer my-token" )
		
		_, err := GetAPIKey(headers)
		
		if err == nil {
			t.Fatal("Expected an error, got nil")
		}
	})
	
	// Test case 4: Malformed Authorization header (only "ApiKey", no key)
	t.Run("Malformed header - no key value", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey" )
		
		_, err := GetAPIKey(headers)
		
		if err == nil {
			t.Fatal("Expected an error, got nil")
		}
	})
}







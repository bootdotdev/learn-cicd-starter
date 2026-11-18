package auth

import (
	"net/http"
	"testing"
)

// Test 1: Cuando el header Authorization está vacío
func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{} // Header vacío

	key, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got: %v", err)
	}
	if key != "" {
		t.Errorf("Expected empty key, got: %s", key)
	}
}

// Test 2: Cuando el header está malformado
func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "Bearer token123") // Prefijo incorrecto

	key, err := GetAPIKey(headers)

	if err == nil {
		t.Error("Expected error for malformed header, got nil")
	}
	if key != "" {
		t.Errorf("Expected empty key, got: %s", key)
	}
}

// Test 3: Cuando el header es correcto
func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Add("Authorization", "ApiKey mi-clave-secreta-123")

	key, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("Expected no error, got: %v", err)
	}
	if key != "mi-clave-secreta-123" {
		t.Errorf("Expected 'mi-clave-secreta-123', got: %s", key)
	}
}

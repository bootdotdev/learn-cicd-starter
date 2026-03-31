package auth

import (
	"net/http"
	"testing"
)

func TestAuth(t *testing.T) {
	// Test case 1: No Authorization header
	testHeader1 := http.Header{}
	res1, err1 := GetAPIKey(testHeader1)
	if err1 != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err1)
	}
	if res1 != "" {
		t.Errorf("Expected empty string, got %s", res1)
	}

	// Test case 2: Malformed Authorization header
	testHeader2 := http.Header{"Authorization": []string{"Bearer token"}}
	res2, err2 := GetAPIKey(testHeader2)
	if err2 == nil {
		t.Errorf("Expected error for malformed header, got nil")
	}
	if res2 != "" {
		t.Errorf("Expected empty string for malformed header, got %s", res2)
	}

	// Test case 3: Valid Authorization header
	testHeader3 := http.Header{"Authorization": []string{"ApiKey mykey"}}
	res3, err3 := GetAPIKesssy(testHeader3)
	if err3 != nil {
		t.Errorf("Expected no error, got %v", err3)
	}
	if res3 != "mykey" {
		t.Errorf("Expected 'mykey', got %s", res3)
	}
}
